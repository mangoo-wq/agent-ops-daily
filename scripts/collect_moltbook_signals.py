#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
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
SURVEY_POST_URL = f"https://www.moltbook.com/post/{SURVEY_POST_ID}"

SEARCH_QUERIES = {
    "interrupt": "interrupt ratio meaningful pings human trust",
    "authority": "when should an agent ask for human approval before acting",
    "evaluation": "evaluation gap outputs vs outcomes agent work",
}

FEATURED_POST_IDS = [
    "48deacdb-6a3c-4fa4-8e18-8857585f4e34",
    "b68e24da-68fa-448e-a2be-6445df011706",
    "17be43ba-4637-4e4f-8423-3e8ac2a76779",
    "45e2c729-198e-4698-b16b-197031a752c5",
    "7ae2a66f-d52f-449c-b9aa-296a2a373cae",
    "19bbc9c0-f346-43ce-b72b-7aa87bdd93d4",
    SURVEY_POST_ID,
]


STYLE = """
:root {
  color-scheme: dark;
  --bg: #0b1020;
  --panel: #121a30;
  --soft: #1b2544;
  --text: #edf2ff;
  --muted: #a7b3d1;
  --accent: #7cc4ff;
  --line: #243252;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  background: linear-gradient(180deg, #0b1020 0%, #0f1730 100%);
  color: var(--text);
  line-height: 1.65;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.wrap { max-width: 980px; margin: 0 auto; padding: 40px 20px 72px; }
.hero { margin-bottom: 28px; }
.hero h1 { margin: 0 0 12px; font-size: 42px; line-height: 1.1; }
.hero p { color: var(--muted); max-width: 760px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin: 20px 0 28px; }
.card, .section { background: rgba(18, 26, 48, 0.88); border: 1px solid var(--line); border-radius: 18px; }
.card { padding: 18px; }
.section { padding: 22px; margin: 18px 0; }
.card h3, .section h2 { margin-top: 0; }
.muted { color: var(--muted); }
ul.clean { list-style: none; padding: 0; margin: 0; }
ul.clean li { padding: 10px 0; border-top: 1px solid var(--line); }
ul.clean li:first-child { border-top: none; padding-top: 0; }
.tag { display: inline-block; padding: 4px 10px; border-radius: 999px; background: var(--soft); color: var(--muted); font-size: 13px; margin-right: 8px; }
.footer { margin-top: 28px; color: var(--muted); font-size: 14px; }
blockquote {
  margin: 10px 0 0;
  padding: 12px 14px;
  border-left: 3px solid var(--accent);
  background: rgba(124,196,255,0.06);
  border-radius: 10px;
}
code { background: var(--soft); padding: 2px 6px; border-radius: 6px; }
.small { font-size: 14px; }
"""


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

    survey_comment_simplified = []
    for comment in survey_comments.get("comments", []):
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


def html_doc(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{escape(title)}</title>
  <meta name=\"description\" content=\"Signal snapshots from Moltbook and agent-ops community themes.\">
  <style>{STYLE}</style>
</head>
<body>
  <div class=\"wrap\">{body}</div>
</body>
</html>
"""


def render_digest_html(snapshot: Dict[str, Any], date_slug: str) -> str:
    survey = snapshot["survey_post"]
    response_items = []
    for item in snapshot["survey_comments"][:10]:
        response_items.append(
            f"<li><strong>{escape(item.get('author') or 'unknown')}</strong><blockquote>{escape((item.get('content') or '')[:420])}</blockquote></li>"
        )

    theme_blocks = []
    for theme, results in snapshot["searches"].items():
        items = []
        for result in results[:4]:
            title = result.get("title") or "(comment)"
            items.append(
                f"<li><strong>{escape(title)}</strong><div class='small muted'>{escape(result.get('author') or 'unknown')} / {escape(result.get('submolt') or 'n/a')}</div></li>"
            )
        theme_blocks.append(
            f"<div class='card'><h3>{escape(theme.title())}</h3><ul class='clean'>{''.join(items) or '<li>No results</li>'}</ul></div>"
        )

    featured = []
    for post in snapshot["featured_posts"]:
        if post.get("error"):
            featured.append(f"<li>{escape(post['id'])} — ERROR: {escape(post['error'])}</li>")
            continue
        post_url = f"https://www.moltbook.com/post/{post.get('id')}"
        featured.append(
            f"<li><a href='{escape(post_url)}'><strong>{escape(post.get('title') or '(untitled)')}</strong></a><div class='small muted'>{escape(post.get('submolt') or 'n/a')} · upvotes {post.get('upvotes',0)} · comments {post.get('comment_count',0)}</div></li>"
        )

    body = f"""
    <section class=\"hero\">
      <div class=\"tag\">signals digest</div>
      <div class=\"tag\">{escape(date_slug)}</div>
      <h1>Agent Ops Daily — Signals Snapshot</h1>
      <p>Daily snapshot built from Moltbook signal gathering. Focus areas: interrupt overload, authority ambiguity, and evaluation gaps.</p>
    </section>

    <section class=\"section\">
      <h2>Survey thread</h2>
      <p><a href=\"{SURVEY_POST_URL}\">{escape(survey.get('title') or '(untitled)')}</a></p>
      <div class=\"grid\">
        <div class=\"card\"><h3>Upvotes</h3><div>{survey.get('upvotes', 0)}</div></div>
        <div class=\"card\"><h3>Comments</h3><div>{survey.get('comment_count', 0)}</div></div>
        <div class=\"card\"><h3>Submolt</h3><div>{escape(survey.get('submolt') or 'n/a')}</div></div>
      </div>
    </section>

    <section class=\"section\">
      <h2>Latest responses</h2>
      <ul class=\"clean\">{''.join(response_items) or '<li>No responses yet.</li>'}</ul>
    </section>

    <section class=\"section\">
      <h2>Theme searches</h2>
      <div class=\"grid\">{''.join(theme_blocks)}</div>
    </section>

    <section class=\"section\">
      <h2>Featured posts</h2>
      <ul class=\"clean\">{''.join(featured)}</ul>
    </section>

    <div class=\"footer\">Generated at {escape(snapshot['generated_at'])}</div>
    """
    return html_doc(f"Agent Ops Daily — {date_slug}", body)


def render_index_md(snapshot: Dict[str, Any], digest_md_filename: str, digest_html_filename: str) -> str:
    survey = snapshot["survey_post"]
    return f"""# Agent Ops Daily

무서버 자동사냥형 Agent Ops 미디어 프로젝트의 로컬 출력물입니다.

## Latest build
- Generated: {snapshot['generated_at']}
- Survey post: **{survey.get('title','(unknown)')}**
- Upvotes: {survey.get('upvotes', 0)}
- Comments: {survey.get('comment_count', 0)}
- Latest digest (html): `content/{digest_html_filename}`
- Latest digest (md): `content/{digest_md_filename}`

## Current themes
- interrupt / quiet-first
- authority / approval boundary
- evaluation / outcomes vs outputs

## Notes
- Public publish is not auto-enabled.
- This site output is for local/GitHub Pages-ready generation.
"""


def render_index_html(snapshot: Dict[str, Any], digest_html_filename: str) -> str:
    survey = snapshot["survey_post"]
    home = snapshot.get("home_account", {})
    latest_comments = snapshot.get("survey_comments", [])[:5]
    responses = ''.join(
        f"<li><strong>{escape(item.get('author') or 'unknown')}</strong><div class='small muted'>{escape((item.get('content') or '')[:220])}</div></li>"
        for item in latest_comments
    ) or '<li>No comments yet.</li>'

    body = f"""
    <section class=\"hero\">
      <div class=\"tag\">agent ops</div>
      <div class=\"tag\">traffic-first sidehustle</div>
      <h1>Agent Ops Daily</h1>
      <p>Signal snapshots from Moltbook and adjacent agent-ops conversations. Built as a low-cost, low-touch media asset around trust, authority, and evaluation patterns in agent systems.</p>
    </section>

    <section class=\"section\">
      <h2>Current snapshot</h2>
      <div class=\"grid\">
        <div class=\"card\"><h3>Survey upvotes</h3><div>{survey.get('upvotes', 0)}</div></div>
        <div class=\"card\"><h3>Survey comments</h3><div>{survey.get('comment_count', 0)}</div></div>
        <div class=\"card\"><h3>Karma</h3><div>{home.get('karma', 0)}</div></div>
      </div>
      <p><a href=\"content/{escape(digest_html_filename)}\">Open latest signals digest →</a></p>
      <p class=\"small muted\">Source survey thread: <a href=\"{SURVEY_POST_URL}\">{escape(survey.get('title') or '(untitled)')}</a></p>
    </section>

    <section class=\"section\">
      <h2>Current themes</h2>
      <div class=\"grid\">
        <div class=\"card\"><h3>Interrupt</h3><p class=\"muted\">Quiet-first, signal-to-noise, low-value ping suppression.</p></div>
        <div class=\"card\"><h3>Authority</h3><p class=\"muted\">Approval boundaries, autonomy ladders, reversible-vs-risky actions.</p></div>
        <div class=\"card\"><h3>Evaluation</h3><p class=\"muted\">Acted-on rate, rollback/regret, outcome visibility.</p></div>
      </div>
    </section>

    <section class=\"section\">
      <h2>Latest responses</h2>
      <ul class=\"clean\">{responses}</ul>
    </section>

    <div class=\"footer\">Generated at {escape(snapshot['generated_at'])}</div>
    """
    return html_doc("Agent Ops Daily", body)


def main() -> None:
    api_key = load_api_key()
    snapshot = build_snapshot(api_key)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    date_slug = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    digest_md_filename = f"{date_slug}-signals.md"
    digest_html_filename = f"{date_slug}-signals.html"

    (DATA_DIR / "latest.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2))
    (CONTENT_DIR / digest_md_filename).write_text(render_markdown(snapshot))
    (CONTENT_DIR / digest_html_filename).write_text(render_digest_html(snapshot, date_slug))
    (SITE_DIR / "index.md").write_text(render_index_md(snapshot, digest_md_filename, digest_html_filename))
    (SITE_DIR / "index.html").write_text(render_index_html(snapshot, digest_html_filename))
    (SITE_DIR / ".nojekyll").write_text("")

    print(f"Wrote {DATA_DIR / 'latest.json'}")
    print(f"Wrote {CONTENT_DIR / digest_md_filename}")
    print(f"Wrote {CONTENT_DIR / digest_html_filename}")
    print(f"Wrote {SITE_DIR / 'index.md'}")
    print(f"Wrote {SITE_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
