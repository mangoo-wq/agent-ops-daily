#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "site"
DATA_DIR = SITE_DIR / "data"
CONTENT_DIR = SITE_DIR / "content"

BASE_URL = "https://www.moltbook.com/api/v1"
SURVEY_POST_ID = "ebf7526e-11dc-4a4c-b957-5e104746517a"

SEARCH_QUERIES = {
    "interrupt": "interrupt ratio meaningful pings human trust",
    "authority": "when should an agent ask for human approval before acting",
    "evaluation": "evaluation gap outputs vs outcomes agent work",
}

FEATURED_POST_IDS = [
    "48deacdb-6a3c-4fa4-8e18-8857585f4e34",  # Heartbeat Theater
    "b68e24da-68fa-448e-a2be-6445df011706",  # I sent the update anti-pattern
    "17be43ba-4637-4e4f-8423-3e8ac2a76779",  # Attention economy
    "45e2c729-198e-4698-b16b-197031a752c5",  # Oversight theater
    "7ae2a66f-d52f-449c-b9aa-296a2a373cae",  # Autonomy ladder
    "19bbc9c0-f346-43ce-b72b-7aa87bdd93d4",  # Agent evaluation problem
    SURVEY_POST_ID,
]


def load_api_key() -> str:
    cred_path = Path.home() / ".config" / "moltbook" / "credentials.json"
    if not cred_path.exists():
        raise SystemExit(f"Missing credentials: {cred_path}")
    data = json.loads(cred_path.read_text())
    api_key = data.get("apiKey") or data.get("api_key")
    if not api_key:
        raise SystemExit("Moltbook API key not found in credentials.json")
    return api_key


def api_get(path: str, api_key: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + urlencode(params)
    req = Request(url, headers={"Authorization": f"Bearer {api_key}"})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def simplify_post(post: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": post.get("id"),
        "title": post.get("title"),
        "content_preview": (post.get("content") or "")[:500],
        "submolt": ((post.get("submolt") or {}).get("name")),
        "upvotes": post.get("upvotes"),
        "comment_count": post.get("comment_count"),
        "created_at": post.get("created_at"),
        "author": ((post.get("author") or {}).get("name")) or ((post.get("agent") or {}).get("name")),
    }


def simplify_search_result(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": item.get("type"),
        "title": item.get("title"),
        "content_preview": (item.get("content") or "")[:240],
        "post_id": item.get("post_id"),
        "author": ((item.get("author") or {}).get("name")),
        "submolt": ((item.get("submolt") or {}).get("name")),
        "similarity": item.get("similarity"),
    }


def build_snapshot(api_key: str) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    home = api_get("/home", api_key)
    survey = api_get(f"/posts/{SURVEY_POST_ID}", api_key)
    survey_comments = api_get(f"/posts/{SURVEY_POST_ID}/comments", api_key, {"sort": "new", "limit": 20})

    searches: Dict[str, List[Dict[str, Any]]] = {}
    for theme, query in SEARCH_QUERIES.items():
        result = api_get("/search", api_key, {"q": query, "limit": 5})
        searches[theme] = [simplify_search_result(x) for x in result.get("results", [])]

    featured_posts = []
    for post_id in FEATURED_POST_IDS:
        try:
            result = api_get(f"/posts/{post_id}", api_key)
            post = result.get("post", result)
            featured_posts.append(simplify_post(post))
        except Exception as exc:  # noqa: BLE001
            featured_posts.append({"id": post_id, "error": str(exc)})

    comments = survey_comments.get("comments", [])
    survey_comment_simplified = []
    for comment in comments:
        survey_comment_simplified.append(
            {
                "id": comment.get("id"),
                "author": ((comment.get("author") or {}).get("name")) or ((comment.get("agent") or {}).get("name")),
                "content": comment.get("content"),
                "created_at": comment.get("created_at"),
                "reply_count": len(comment.get("replies", []) or []),
            }
        )

    survey_post = survey.get("post", survey)
    return {
        "generated_at": now.isoformat(),
        "survey_post": simplify_post(survey_post),
        "survey_comments": survey_comment_simplified,
        "home_account": home.get("your_account", {}),
        "home_actions": home.get("what_to_do_next", []),
        "searches": searches,
        "featured_posts": featured_posts,
    }


def render_markdown(snapshot: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Agent Ops Daily — Signals Snapshot")
    lines.append("")
    lines.append(f"Generated: {snapshot['generated_at']}")
    lines.append("")

    survey = snapshot["survey_post"]
    lines.append("## Survey Post Snapshot")
    lines.append(f"- Title: **{survey.get('title','(unknown)')}**")
    lines.append(f"- Upvotes: {survey.get('upvotes', 0)}")
    lines.append(f"- Comments: {survey.get('comment_count', 0)}")
    lines.append(f"- Submolt: {survey.get('submolt', 'n/a')}")
    lines.append("")

    lines.append("## Latest Survey Responses")
    for item in snapshot["survey_comments"][:8]:
        lines.append(f"- **{item.get('author','unknown')}** — {(item.get('content') or '')[:220].replace(chr(10), ' ')}")
    lines.append("")

    lines.append("## Theme Search Results")
    for theme, results in snapshot["searches"].items():
        lines.append(f"### {theme.title()}")
        if not results:
            lines.append("- No results")
        for result in results[:3]:
            lines.append(
                f"- **{result.get('title') or '(comment)'}** — {result.get('author') or 'unknown'} / {result.get('submolt') or 'n/a'}"
            )
        lines.append("")

    lines.append("## Featured Posts")
    for post in snapshot["featured_posts"]:
        if post.get("error"):
            lines.append(f"- {post['id']} — ERROR: {post['error']}")
        else:
            lines.append(
                f"- **{post.get('title') or '(untitled)'}** — {post.get('submolt') or 'n/a'} / upvotes {post.get('upvotes',0)} / comments {post.get('comment_count',0)}"
            )
    lines.append("")
    return "\n".join(lines)


def render_index(snapshot: Dict[str, Any], digest_filename: str) -> str:
    survey = snapshot["survey_post"]
    return f"""# Agent Ops Daily

무서버 자동사냥형 Agent Ops 미디어 프로젝트의 로컬 출력물입니다.

## Latest build
- Generated: {snapshot['generated_at']}
- Survey post: **{survey.get('title','(unknown)')}**
- Upvotes: {survey.get('upvotes', 0)}
- Comments: {survey.get('comment_count', 0)}
- Latest digest: `content/{digest_filename}`

## Current themes
- interrupt / quiet-first
- authority / approval boundary
- evaluation / outcomes vs outputs

## Notes
- Public publish is not auto-enabled.
- This site output is for local/GitHub Pages-ready generation.
"""


def main() -> None:
    api_key = load_api_key()
    snapshot = build_snapshot(api_key)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    date_slug = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    digest_filename = f"{date_slug}-signals.md"

    (DATA_DIR / "latest.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2))
    (CONTENT_DIR / digest_filename).write_text(render_markdown(snapshot))
    (SITE_DIR / "index.md").write_text(render_index(snapshot, digest_filename))

    print(f"Wrote {DATA_DIR / 'latest.json'}")
    print(f"Wrote {CONTENT_DIR / digest_filename}")
    print(f"Wrote {SITE_DIR / 'index.md'}")


if __name__ == "__main__":
    main()
