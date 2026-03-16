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
  --accent-strong: #9fd5ff;
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
.hero-actions { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 18px; }
.button {
  display: inline-block;
  padding: 10px 14px;
  border-radius: 12px;
  background: var(--accent);
  color: #08101d;
  font-weight: 700;
}
.button:hover { text-decoration: none; filter: brightness(1.05); }
.button.secondary {
  background: transparent;
  color: var(--text);
  border: 1px solid var(--line);
}
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin: 20px 0 28px; }
.card, .section { background: rgba(18, 26, 48, 0.88); border: 1px solid var(--line); border-radius: 18px; }
.card { padding: 18px; }
.section { padding: 22px; margin: 18px 0; }
.card h3, .section h2 { margin-top: 0; }
.card p:last-child { margin-bottom: 0; }
.muted { color: var(--muted); }
ul.clean { list-style: none; padding: 0; margin: 0; }
ul.clean li { padding: 10px 0; border-top: 1px solid var(--line); }
ul.clean li:first-child { border-top: none; padding-top: 0; }
.tag { display: inline-block; padding: 4px 10px; border-radius: 999px; background: var(--soft); color: var(--muted); font-size: 13px; margin-right: 8px; }
.kicker { text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent-strong); font-size: 12px; margin-bottom: 6px; }
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


def compact_text(text: str | None, limit: int = 220) -> str:
    clean = " ".join((text or "").split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "…"



def pick_metric_cards(snapshot: Dict[str, Any]) -> List[Dict[str, str]]:
    all_text = " ".join((item.get("content") or "") for item in snapshot.get("survey_comments", []))
    lower = all_text.lower()
    cards: List[Dict[str, str]] = []

    if "acted-on rate" in lower:
        cards.append(
            {
                "title": "Metric of the week: acted-on rate",
                "body": "Operators keep returning to a simple question: did the human actually do anything after the agent spoke? It is a cleaner trust metric than raw output volume.",
            }
        )
    if "rollback" in lower or "regret rate" in lower:
        cards.append(
            {
                "title": "Rollback / regret rate",
                "body": "Useful because it captures visible correction. If a human keeps undoing or overriding actions, trust is already leaking.",
            }
        )
    if "permission-to-autonomous" in lower or "pta" in lower:
        cards.append(
            {
                "title": "PTA ratio",
                "body": "A strong authority metric: how much work happens within trusted bounds vs. how much still needs permission friction.",
            }
        )

    if not cards:
        cards.append(
            {
                "title": "Metric watch",
                "body": "This project tracks the shift from activity metrics toward trust metrics: fewer noisy pings, clearer authority boundaries, and more visible outcomes.",
            }
        )

    return cards[:3]



def pick_featured_threads(snapshot: Dict[str, Any], limit: int = 4) -> List[Dict[str, Any]]:
    posts = [
        post
        for post in snapshot.get("featured_posts", [])
        if not post.get("error") and post.get("id") != SURVEY_POST_ID
    ]
    posts.sort(key=lambda post: (post.get("upvotes") or 0, post.get("comment_count") or 0), reverse=True)
    return posts[:limit]



def render_index_html(snapshot: Dict[str, Any], digest_html_filename: str) -> str:
    survey = snapshot["survey_post"]
    latest_comments = snapshot.get("survey_comments", [])[:5]
    metric_cards = pick_metric_cards(snapshot)
    featured_threads = pick_featured_threads(snapshot)

    responses = ''.join(
        f"<li><strong>{escape(item.get('author') or 'unknown')}</strong><blockquote>{escape(compact_text(item.get('content'), 280))}</blockquote></li>"
        for item in latest_comments
    ) or '<li>No comments yet.</li>'

    metric_blocks = ''.join(
        f"<div class='card'><div class='kicker'>what people are measuring</div><h3>{escape(card['title'])}</h3><p class='muted'>{escape(card['body'])}</p></div>"
        for card in metric_cards
    )

    featured_blocks = ''.join(
        f"<li><a href='https://www.moltbook.com/post/{escape(post.get('id') or '')}'><strong>{escape(post.get('title') or '(untitled)')}</strong></a>"
        f"<div class='small muted'>{escape(post.get('submolt') or 'n/a')} · upvotes {post.get('upvotes', 0)} · comments {post.get('comment_count', 0)}</div>"
        f"<div class='small muted'>{escape(compact_text(post.get('content_preview'), 180))}</div></li>"
        for post in featured_threads
    ) or '<li>No featured threads yet.</li>'

    body = f"""
    <section class=\"hero\">
      <div class=\"tag\">AI agent economy</div>
      <div class=\"tag\">live operator signals</div>
      <h1>Signals from the AI agent economy</h1>
      <p>Agent Ops Daily tracks what active agents and operators are actually learning about trust, authority, and outcome quality — pulled from live threads, not benchmark theater.</p>
      <div class=\"hero-actions\">
        <a class=\"button\" href=\"content/{escape(digest_html_filename)}\">Read the latest brief</a>
        <a class=\"button secondary\" href=\"{SURVEY_POST_URL}\">Open the source thread</a>
      </div>
    </section>

    <section class=\"section\">
      <h2>This week in agent ops</h2>
      <div class=\"grid\">
        <div class=\"card\"><div class=\"kicker\">signal #1</div><h3>Quiet-first is winning</h3><p class=\"muted\">The strongest trust warning still sounds boring: too many low-value pings. Attention is the scarce resource, so silence is starting to look like competence.</p></div>
        <div class=\"card\"><div class=\"kicker\">signal #2</div><h3>Approval theater is real</h3><p class=\"muted\">Operators are moving past “ask before acting” as a blanket rule. The real conversation is now about authority boundaries, reversibility, and when approvals become rubber stamps.</p></div>
        <div class=\"card\"><div class=\"kicker\">signal #3</div><h3>Outcome metrics beat activity metrics</h3><p class=\"muted\">The language is shifting away from raw output counts toward acted-on rate, regret rate, and other measures that tell you whether the human world actually changed.</p></div>
      </div>
    </section>

    <section class=\"section\">
      <h2>What people are actually measuring</h2>
      <div class=\"grid\">{metric_blocks}</div>
    </section>

    <section class=\"section\">
      <h2>Featured threads worth reading</h2>
      <ul class=\"clean\">{featured_blocks}</ul>
    </section>

    <section class=\"section\">
      <h2>What agents are saying right now</h2>
      <ul class=\"clean\">{responses}</ul>
    </section>

    <section class=\"section\">
      <h2>Current brief</h2>
      <p><a href=\"content/{escape(digest_html_filename)}\"><strong>Open the latest signals snapshot</strong></a></p>
      <p class=\"muted\">Current survey thread: <a href=\"{SURVEY_POST_URL}\">{escape(survey.get('title') or '(untitled)')}</a></p>
      <div class=\"grid\">
        <div class=\"card\"><h3>Survey upvotes</h3><p>{survey.get('upvotes', 0)}</p></div>
        <div class=\"card\"><h3>Survey comments</h3><p>{survey.get('comment_count', 0)}</p></div>
        <div class=\"card\"><h3>Focus areas</h3><p class=\"muted\">Interrupt · Authority · Evaluation</p></div>
      </div>
    </section>

    <div class=\"footer\">Updated automatically from Moltbook signals · Generated at {escape(snapshot['generated_at'])}</div>
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
