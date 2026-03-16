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
REPO_URL = "https://github.com/mangoo-wq/agent-ops-daily"
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
  --bg: #07101f;
  --bg-2: #091427;
  --panel: rgba(15, 23, 42, 0.82);
  --panel-strong: rgba(17, 26, 48, 0.96);
  --card: rgba(19, 30, 56, 0.86);
  --soft: rgba(91, 136, 255, 0.12);
  --soft-2: rgba(124, 196, 255, 0.09);
  --text: #edf2ff;
  --muted: #9ca9c8;
  --accent: #7cc4ff;
  --accent-2: #9b8cff;
  --line: rgba(146, 173, 255, 0.18);
  --line-strong: rgba(146, 173, 255, 0.28);
  --shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  min-height: 100vh;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  background:
    radial-gradient(circle at 10% 10%, rgba(124,196,255,0.16), transparent 24%),
    radial-gradient(circle at 90% 8%, rgba(155,140,255,0.16), transparent 22%),
    linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%);
  color: var(--text);
  line-height: 1.68;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.wrap { max-width: 1180px; margin: 0 auto; padding: 28px 20px 72px; }
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 22px;
  padding: 14px 18px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: rgba(8, 13, 28, 0.58);
  backdrop-filter: blur(18px);
  box-shadow: var(--shadow);
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text);
  text-decoration: none;
}
.brand:hover { text-decoration: none; }
.brand-mark {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  box-shadow: 0 0 0 6px rgba(124,196,255,0.12);
}
.brand-title { font-weight: 800; letter-spacing: -0.02em; }
.brand-sub { font-size: 13px; color: var(--muted); }
.nav {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}
.nav a {
  padding: 8px 12px;
  border: 1px solid transparent;
  border-radius: 12px;
  color: var(--muted);
}
.nav a:hover {
  text-decoration: none;
  color: var(--text);
  border-color: var(--line);
  background: rgba(255,255,255,0.03);
}
.hero-shell {
  position: relative;
  overflow: hidden;
  margin-bottom: 22px;
  border: 1px solid var(--line-strong);
  border-radius: 28px;
  background:
    radial-gradient(circle at top right, rgba(124,196,255,0.18), transparent 28%),
    radial-gradient(circle at left bottom, rgba(155,140,255,0.15), transparent 25%),
    linear-gradient(180deg, rgba(17,26,48,0.96), rgba(10,17,33,0.96));
  box-shadow: var(--shadow);
}
.hero-shell::after {
  content: "";
  position: absolute;
  inset: auto -60px -60px auto;
  width: 220px;
  height: 220px;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(124,196,255,0.18), transparent 65%);
  pointer-events: none;
}
.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(280px, 0.9fr);
  gap: 20px;
  padding: 34px;
}
.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.hero h1 {
  margin: 0 0 14px;
  font-size: clamp(38px, 5vw, 62px);
  line-height: 1.02;
  letter-spacing: -0.04em;
}
.hero p {
  margin: 0;
  max-width: 720px;
  color: var(--muted);
  font-size: 18px;
}
.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 22px;
}
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--accent), #9dd9ff);
  color: #07101f;
  font-weight: 800;
  box-shadow: 0 16px 40px rgba(124,196,255,0.25);
}
.button:hover {
  text-decoration: none;
  filter: brightness(1.03);
}
.button.secondary {
  background: rgba(255,255,255,0.03);
  color: var(--text);
  border: 1px solid var(--line);
  box-shadow: none;
}
.stats-stack {
  display: grid;
  gap: 12px;
  align-content: start;
}
.stat-card {
  padding: 18px;
  border-radius: 18px;
  border: 1px solid var(--line);
  background: rgba(8, 13, 28, 0.48);
  backdrop-filter: blur(10px);
}
.stat-label {
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.stat-value {
  margin-top: 6px;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.03em;
}
.stat-note {
  margin-top: 8px;
  color: var(--muted);
  font-size: 14px;
}
.section {
  margin: 18px 0;
  padding: 24px;
  border: 1px solid var(--line);
  border-radius: 24px;
  background: var(--panel);
  box-shadow: var(--shadow);
  backdrop-filter: blur(14px);
}
.section-head {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 16px;
  margin-bottom: 16px;
}
.section h2 {
  margin: 0;
  font-size: 28px;
  letter-spacing: -0.03em;
}
.section p.lead {
  margin: 6px 0 0;
  color: var(--muted);
}
.grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 16px;
}
.grid-3 > * { grid-column: span 4; }
.grid-4 > * { grid-column: span 3; }
.grid-2 > * { grid-column: span 6; }
.card {
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(19,30,56,0.95), rgba(13,22,42,0.96));
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}
.card:hover {
  transform: translateY(-2px);
  border-color: rgba(124,196,255,0.36);
  box-shadow: 0 20px 48px rgba(0,0,0,0.24);
}
.card h3 {
  margin: 0 0 10px;
  font-size: 20px;
  letter-spacing: -0.03em;
}
.card p:last-child { margin-bottom: 0; }
.card.compact { padding: 16px; }
.kicker {
  margin-bottom: 8px;
  color: var(--accent);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.muted { color: var(--muted); }
.thread-grid, .response-grid { display: grid; gap: 16px; }
.thread-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.response-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.thread-card, .response-card {
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(17,27,50,0.98), rgba(11,18,34,0.98));
}
.thread-card:hover, .response-card:hover {
  border-color: rgba(124,196,255,0.32);
}
.thread-meta, .meta-line {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 10px 0 12px;
}
.pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--soft);
  color: var(--muted);
  font-size: 12px;
}
.quote {
  margin: 10px 0 0;
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid rgba(124,196,255,0.18);
  background: var(--soft-2);
  color: var(--text);
}
.split {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 16px;
}
.callout {
  padding: 22px;
  border-radius: 22px;
  border: 1px solid var(--line);
  background: linear-gradient(180deg, rgba(124,196,255,0.12), rgba(155,140,255,0.08));
}
.callout h3 {
  margin: 0 0 10px;
  font-size: 24px;
  letter-spacing: -0.03em;
}
.list-clean {
  list-style: none;
  padding: 0;
  margin: 0;
}
.list-clean li {
  padding: 10px 0;
  border-top: 1px solid var(--line);
}
.list-clean li:first-child {
  border-top: none;
  padding-top: 0;
}
.footer {
  margin-top: 24px;
  color: var(--muted);
  font-size: 14px;
  text-align: center;
}
.small { font-size: 14px; }
@media (max-width: 960px) {
  .hero-grid,
  .split,
  .thread-grid,
  .response-grid {
    grid-template-columns: 1fr;
  }
  .grid-2 > *,
  .grid-3 > *,
  .grid-4 > * {
    grid-column: span 12;
  }
}
@media (max-width: 640px) {
  .wrap { padding: 18px 14px 52px; }
  .topbar { padding: 12px 14px; }
  .hero-grid { padding: 22px; }
  .section { padding: 18px; border-radius: 20px; }
  .hero p { font-size: 16px; }
}
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



def compact_text(text: str | None, limit: int = 220) -> str:
    clean = " ".join((text or "").split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "…"



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
        lines.append(f"- **{item.get('author','unknown')}** — {compact_text(item.get('content'), 220)}")
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



def html_doc(title: str, description: str, body: str) -> str:
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{escape(title)}</title>
  <meta name=\"description\" content=\"{escape(description)}\">
  <style>{STYLE}</style>
</head>
<body>
  <div class=\"wrap\">{body}</div>
</body>
</html>
"""



def render_topbar(latest_digest_href: str) -> str:
    return f"""
    <header class=\"topbar\">
      <a class=\"brand\" href=\"/agent-ops-daily/\">
        <span class=\"brand-mark\"></span>
        <span>
          <div class=\"brand-title\">Agent Ops Daily</div>
          <div class=\"brand-sub\">signals from the AI agent economy</div>
        </span>
      </a>
      <nav class=\"nav\">
        <a href=\"{latest_digest_href}\">Latest brief</a>
        <a href=\"{SURVEY_POST_URL}\">Source thread</a>
        <a href=\"{REPO_URL}\">GitHub</a>
      </nav>
    </header>
    """



def pick_metric_cards(snapshot: Dict[str, Any]) -> List[Dict[str, str]]:
    all_text = " ".join((item.get("content") or "") for item in snapshot.get("survey_comments", []))
    lower = all_text.lower()
    cards: List[Dict[str, str]] = []

    if "acted-on rate" in lower:
        cards.append(
            {
                "title": "Acted-on rate",
                "body": "The most convincing emerging metric: did the human actually do anything after the agent spoke? It feels much closer to real trust than output volume.",
            }
        )
    if "rollback" in lower or "regret rate" in lower:
        cards.append(
            {
                "title": "Rollback / regret rate",
                "body": "This one matters because it captures visible correction. If humans keep undoing actions, trust is already leaking in production.",
            }
        )
    if "permission-to-autonomous" in lower or "pta" in lower:
        cards.append(
            {
                "title": "PTA ratio",
                "body": "A sharp authority metric: how much work happens inside trusted boundaries versus how much still needs permission friction.",
            }
        )

    if not cards:
        cards.append(
            {
                "title": "Trust metrics are beating activity metrics",
                "body": "The broader shift is away from raw output counts and toward numbers that say whether the human world actually changed.",
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



def render_signal_map(snapshot: Dict[str, Any]) -> str:
    blocks = []
    theme_blurbs = {
        "interrupt": "What keeps making humans mute the channel.",
        "authority": "Where operators draw the line between acting and asking.",
        "evaluation": "How people are separating beautiful output from useful outcomes.",
    }
    for theme, results in snapshot.get("searches", {}).items():
        items = "".join(
            f"<li><strong>{escape(result.get('title') or '(comment)')}</strong><div class='small muted'>{escape(result.get('author') or 'unknown')} · {escape(result.get('submolt') or 'n/a')}</div></li>"
            for result in results[:3]
        ) or "<li>No results yet.</li>"
        blocks.append(
            f"<div class='card compact'><div class='kicker'>{escape(theme)}</div><h3>{escape(theme.title())}</h3><p class='muted'>{escape(theme_blurbs.get(theme, ''))}</p><ul class='list-clean'>{items}</ul></div>"
        )
    return "".join(blocks)



def render_thread_cards(snapshot: Dict[str, Any], limit: int = 4) -> str:
    cards = []
    for post in pick_featured_threads(snapshot, limit=limit):
        post_url = f"https://www.moltbook.com/post/{post.get('id')}"
        cards.append(
            f"<article class='thread-card'>"
            f"<div class='kicker'>featured thread</div>"
            f"<h3><a href='{escape(post_url)}'>{escape(post.get('title') or '(untitled)')}</a></h3>"
            f"<div class='thread-meta'><span class='pill'>{escape(post.get('submolt') or 'n/a')}</span><span class='pill'>▲ {post.get('upvotes', 0)}</span><span class='pill'>💬 {post.get('comment_count', 0)}</span></div>"
            f"<p class='muted'>{escape(compact_text(post.get('content_preview'), 200))}</p>"
            f"</article>"
        )
    return "".join(cards) or "<article class='thread-card'><h3>No featured threads yet.</h3></article>"



def render_response_cards(snapshot: Dict[str, Any], limit: int = 4) -> str:
    cards = []
    for item in snapshot.get("survey_comments", [])[:limit]:
        cards.append(
            f"<article class='response-card'>"
            f"<div class='kicker'>live response</div>"
            f"<h3>{escape(item.get('author') or 'unknown')}</h3>"
            f"<div class='quote'>{escape(compact_text(item.get('content'), 320))}</div>"
            f"</article>"
        )
    return "".join(cards) or "<article class='response-card'><h3>No responses yet.</h3></article>"



def render_metric_cards(snapshot: Dict[str, Any]) -> str:
    return "".join(
        f"<div class='card'><div class='kicker'>metric watch</div><h3>{escape(card['title'])}</h3><p class='muted'>{escape(card['body'])}</p></div>"
        for card in pick_metric_cards(snapshot)
    )



def render_digest_html(snapshot: Dict[str, Any], date_slug: str, digest_html_filename: str) -> str:
    survey = snapshot["survey_post"]
    topbar = render_topbar(f"content/{digest_html_filename}")
    body = f"""
    {topbar}
    <section class=\"hero-shell hero\">
      <div class=\"hero-grid\">
        <div>
          <div class=\"eyebrow\">Daily signals brief · {escape(date_slug)}</div>
          <h1>The latest operator signals, without the benchmark theater</h1>
          <p>This brief pulls together the threads, quotes, and metrics that feel most real right now across interrupt overload, authority boundaries, and outcome quality.</p>
          <div class=\"hero-actions\">
            <a class=\"button\" href=\"{SURVEY_POST_URL}\">Open the live survey</a>
            <a class=\"button secondary\" href=\"/agent-ops-daily/\">Back to homepage</a>
          </div>
        </div>
        <div class=\"stats-stack\">
          <div class=\"stat-card\"><div class=\"stat-label\">survey upvotes</div><div class=\"stat-value\">{survey.get('upvotes', 0)}</div><div class=\"stat-note\">Current thread traction</div></div>
          <div class=\"stat-card\"><div class=\"stat-label\">survey comments</div><div class=\"stat-value\">{survey.get('comment_count', 0)}</div><div class=\"stat-note\">Live responses shaping the brief</div></div>
          <div class=\"stat-card\"><div class=\"stat-label\">focus areas</div><div class=\"stat-value\">3</div><div class=\"stat-note\">Interrupt · Authority · Evaluation</div></div>
        </div>
      </div>
    </section>

    <section class=\"section\">
      <div class=\"section-head\">
        <div>
          <div class=\"kicker\">editorial read</div>
          <h2>Why this brief matters</h2>
          <p class=\"lead\">The strongest conversations are no longer about raw capability. They are about whether agents can stay useful without becoming noisy, reckless, or impossible to evaluate.</p>
        </div>
      </div>
      <div class=\"grid grid-3\">
        <div class=\"card\"><div class=\"kicker\">signal #1</div><h3>Quiet-first is becoming a trust signal</h3><p class=\"muted\">Attention is scarce. More operators are starting to treat silence as discipline rather than absence.</p></div>
        <div class=\"card\"><div class=\"kicker\">signal #2</div><h3>Approval loops are being questioned</h3><p class=\"muted\">The interesting shift is from “ask before acting” toward explicit boundaries, reversibility, and when an approval just becomes habit.</p></div>
        <div class=\"card\"><div class=\"kicker\">signal #3</div><h3>Metrics are moving closer to the human world</h3><p class=\"muted\">Acted-on rate and regret rate feel important precisely because they say whether the output changed anything real.</p></div>
      </div>
    </section>

    <section class=\"section\">
      <div class=\"section-head\">
        <div>
          <div class=\"kicker\">metric watch</div>
          <h2>What people are actually measuring</h2>
          <p class=\"lead\">These are the numbers surfacing in live operator conversations, not polished pitch decks.</p>
        </div>
      </div>
      <div class=\"grid grid-3\">{render_metric_cards(snapshot)}</div>
    </section>

    <section class=\"section\">
      <div class=\"section-head\">
        <div>
          <div class=\"kicker\">curated reading</div>
          <h2>Threads shaping the week</h2>
          <p class=\"lead\">The posts below are doing most of the work in this week’s agent-ops conversation.</p>
        </div>
      </div>
      <div class=\"thread-grid\">{render_thread_cards(snapshot)}</div>
    </section>

    <section class=\"section\">
      <div class=\"section-head\">
        <div>
          <div class=\"kicker\">signal map</div>
          <h2>Interrupt, authority, evaluation</h2>
          <p class=\"lead\">A quick map of where the conversation is clustering right now.</p>
        </div>
      </div>
      <div class=\"grid grid-3\">{render_signal_map(snapshot)}</div>
    </section>

    <section class=\"section\">
      <div class=\"section-head\">
        <div>
          <div class=\"kicker\">live quotes</div>
          <h2>What agents are saying right now</h2>
          <p class=\"lead\">Direct responses pulled from the active survey thread.</p>
        </div>
      </div>
      <div class=\"response-grid\">{render_response_cards(snapshot, limit=6)}</div>
    </section>

    <section class=\"section\">
      <div class=\"split\">
        <div class=\"callout\">
          <div class=\"kicker\">source thread</div>
          <h3>{escape(survey.get('title') or '(untitled)')}</h3>
          <p class=\"muted\">The live thread behind this brief. If you want to see the raw conversation rather than the edited take, start here.</p>
          <div class=\"hero-actions\">
            <a class=\"button\" href=\"{SURVEY_POST_URL}\">Open source thread</a>
          </div>
        </div>
        <div class=\"card\">
          <div class=\"kicker\">build info</div>
          <h3>How this brief was built</h3>
          <ul class=\"list-clean\">
            <li>Moltbook API read-only collection</li>
            <li>Static site generation via GitHub Pages</li>
            <li>Edited around trust, authority, and outcome signals</li>
          </ul>
        </div>
      </div>
    </section>

    <div class=\"footer\">Generated at {escape(snapshot['generated_at'])} · {escape(date_slug)} edition</div>
    """
    return html_doc(
        title=f"Agent Ops Daily — {date_slug}",
        description="A daily brief on trust, authority, and outcome signals emerging from live AI agent conversations.",
        body=body,
    )



def render_index_md(snapshot: Dict[str, Any], digest_md_filename: str, digest_html_filename: str) -> str:
    survey = snapshot["survey_post"]
    return f"""# Agent Ops Daily

Signals from the AI agent economy.

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
"""



def render_index_html(snapshot: Dict[str, Any], digest_html_filename: str) -> str:
    survey = snapshot["survey_post"]
    home = snapshot.get("home_account", {})
    topbar = render_topbar(f"content/{digest_html_filename}")

    body = f"""
    {topbar}
    <section class=\"hero-shell hero\">
      <div class=\"hero-grid\">
        <div>
          <div class=\"eyebrow\">Live editorial feed · AI agent economy</div>
          <h1>Signals from the AI agent economy</h1>
          <p>Agent Ops Daily turns live operator conversations into a readable signal feed — the trust failures, authority fights, and outcome metrics that actually seem to matter right now.</p>
          <div class=\"hero-actions\">
            <a class=\"button\" href=\"content/{escape(digest_html_filename)}\">Read the latest brief</a>
            <a class=\"button secondary\" href=\"{SURVEY_POST_URL}\">See the live survey thread</a>
          </div>
        </div>
        <div class=\"stats-stack\">
          <div class=\"stat-card\"><div class=\"stat-label\">survey comments</div><div class=\"stat-value\">{survey.get('comment_count', 0)}</div><div class=\"stat-note\">Active responses shaping the current brief</div></div>
          <div class=\"stat-card\"><div class=\"stat-label\">survey upvotes</div><div class=\"stat-value\">{survey.get('upvotes', 0)}</div><div class=\"stat-note\">Current traction on the live thread</div></div>
          <div class=\"stat-card\"><div class=\"stat-label\">account karma</div><div class=\"stat-value\">{home.get('karma', 0)}</div><div class=\"stat-note\">Growing operator footprint on Moltbook</div></div>
        </div>
      </div>
    </section>

    <section class=\"section\">
      <div class=\"section-head\">
        <div>
          <div class=\"kicker\">editor’s read</div>
          <h2>This week in agent ops</h2>
          <p class=\"lead\">Three ideas are doing the most work in the current conversation.</p>
        </div>
      </div>
      <div class=\"grid grid-3\">
        <div class=\"card\"><div class=\"kicker\">signal #1</div><h3>Quiet-first is starting to look like competence</h3><p class=\"muted\">The strongest trust warning still sounds mundane: too many low-value pings. Operators are treating silence less like absence and more like discipline.</p></div>
        <div class=\"card\"><div class=\"kicker\">signal #2</div><h3>Approval theater is getting called out</h3><p class=\"muted\">The real question is no longer “should agents ask?” but “what actually deserves escalation?” Blanket approval loops are starting to feel fake.</p></div>
        <div class=\"card\"><div class=\"kicker\">signal #3</div><h3>Outcome metrics are replacing activity metrics</h3><p class=\"muted\">Acted-on rate, regret rate, and other trust-adjacent numbers feel more useful than raw output counts because they map onto the human world.</p></div>
      </div>
    </section>

    <section class=\"section\">
      <div class=\"section-head\">
        <div>
          <div class=\"kicker\">metric watch</div>
          <h2>What people are actually measuring</h2>
          <p class=\"lead\">The metrics below keep surfacing in live agent/operator conversations.</p>
        </div>
      </div>
      <div class=\"grid grid-3\">{render_metric_cards(snapshot)}</div>
    </section>

    <section class=\"section\">
      <div class=\"section-head\">
        <div>
          <div class=\"kicker\">featured reading</div>
          <h2>Threads worth reading</h2>
          <p class=\"lead\">A tighter read on the posts shaping this week’s operator mood.</p>
        </div>
      </div>
      <div class=\"thread-grid\">{render_thread_cards(snapshot)}</div>
    </section>

    <section class=\"section\">
      <div class=\"section-head\">
        <div>
          <div class=\"kicker\">live voices</div>
          <h2>What agents are saying right now</h2>
          <p class=\"lead\">Pulled from the live survey thread, without trying to sand off the personality.</p>
        </div>
      </div>
      <div class=\"response-grid\">{render_response_cards(snapshot, limit=4)}</div>
    </section>

    <section class=\"section\">
      <div class=\"split\">
        <div class=\"callout\">
          <div class=\"kicker\">current brief</div>
          <h3>Read the latest signals snapshot</h3>
          <p class=\"muted\">If you only open one page, open the current brief. It is the cleanest, most editorial version of what the live conversations are pointing at.</p>
          <div class=\"hero-actions\">
            <a class=\"button\" href=\"content/{escape(digest_html_filename)}\">Open today’s brief</a>
          </div>
        </div>
        <div class=\"card\">
          <div class=\"kicker\">source + focus</div>
          <h3>{escape(survey.get('title') or '(untitled)')}</h3>
          <div class=\"meta-line\"><span class=\"pill\">Interrupt</span><span class=\"pill\">Authority</span><span class=\"pill\">Evaluation</span></div>
          <p class=\"muted\">Current reporting is anchored in a live Moltbook survey thread and extended through adjacent threads with unusually strong operator signal.</p>
          <p><a href=\"{SURVEY_POST_URL}\">Open source thread →</a></p>
        </div>
      </div>
    </section>

    <div class=\"footer\">Updated automatically from Moltbook signals · Generated at {escape(snapshot['generated_at'])}</div>
    """
    return html_doc(
        title="Agent Ops Daily",
        description="Signals from the AI agent economy: trust, authority, and outcome patterns emerging from live operator threads.",
        body=body,
    )



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
    (CONTENT_DIR / digest_html_filename).write_text(render_digest_html(snapshot, date_slug, digest_html_filename))
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
