import html
from .config import ROOT
from .store import now

def snapshot(store):
    e = html.escape
    records = store.records()
    contacts = [r for r in records if r['kind']=='contact']
    posts = [r for r in records if r['kind']=='post']
    runs = [dict(r) for r in store.db.execute('SELECT * FROM runs ORDER BY id DESC LIMIT 20')]
    published = sum(r['status']=='published' for r in posts)
    pending = sum(r['status']=='pending' for r in contacts)
    accepted = sum(r['status']=='accepted' for r in contacts)
    cards = ''
    for r in records:
        if r['kind']=='history': continue
        cards += f'<details><summary><span>{e(r["title"])}</span><b>{e(r["status"])}</b></summary><pre>{e(r["body"])}</pre></details>'
    status = store.setting('api_blocked') or 'Live API not verified — last connection attempt failed'
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>PJ · Career workspace</title>
    <style>*{{box-sizing:border-box}}body{{margin:0;background:#f1f3ed;color:#17372c;font:16px system-ui}}main{{max-width:1100px;margin:auto;padding:60px 28px}}header{{display:flex;justify-content:space-between;align-items:center}}.label{{letter-spacing:.16em;font-size:12px;font-weight:700;color:#55705f}}h1{{font-size:52px;letter-spacing:-2px;margin:18px 0}}.subtitle{{color:#55705f;max-width:650px;line-height:1.7}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:34px 0}}.metric,section{{background:white;border:1px solid #dde5da;border-radius:16px;padding:24px}}.metric strong{{font-size:36px;display:block}}.metric span{{font-size:13px;color:#55705f}}section{{margin:20px 0}}h2{{font-size:22px}}.notice{{background:#fff3dd;border:1px solid #e8d7b2}}details{{border-bottom:1px solid #e0e7de;padding:18px 0}}summary{{display:flex;justify-content:space-between;gap:20px;cursor:pointer}}summary b{{font-size:12px;color:#50715d;background:#edf4eb;padding:4px 9px;border-radius:8px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.65 system-ui}}.pill{{border:1px solid #b5c8b6;padding:9px 15px;border-radius:20px;font-size:13px}}footer{{color:#65786a;font-size:12px;margin-top:28px}}@media(max-width:650px){{.grid{{grid-template-columns:1fr 1fr}}h1{{font-size:36px}}}}</style></head><body><main>
    <header><span class="label">PJ / CAREER ASSISTANT</span><span class="pill">One shared workspace</span></header>
    <h1>Your next chapter,<br>in one place.</h1><p class="subtitle">Career evidence, LinkedIn content, professional contacts and application history. UK · UAE / Dubai · Oman · Qatar · Kuwait.</p>
    <div class="grid"><div class="metric"><strong>{published}</strong><span>Imported published posts</span></div><div class="metric"><strong>{pending}</strong><span>Pending invitations</span></div><div class="metric"><strong>{accepted}</strong><span>Recorded acceptances</span></div><div class="metric"><strong>1</strong><span>Active consolidated schedule</span></div></div>
    <section class="notice"><h2>What needs attention</h2><p>{e(status)}. Local server startup was blocked by the current execution permissions.</p><p>CV evidence is saved. Country-specific work authorisation still needs confirmation.</p><p>This is an offline snapshot. For generation and editing, launch <code>./run.sh serve</code> from the project folder when local execution is permitted.</p></section>
    <section><h2>Less repetition, fewer calls</h2><p>Saved answers are reused. Only the requested specialist runs. Daily slots prevent duplicate drafts. API attempts are capped and quota failures pause generation.</p><p>No invitation, message, application or post is sent by this application.</p></section>
    <section><h2>Shared history</h2>{cards}</section><footer>Snapshot: {e(now())}. Imported observations are historical, not a live LinkedIn status check. Private local data — do not publish this file.</footer></main></body></html>'''
    target = ROOT / 'private' / 'dashboard.html'
    target.write_text(page)
    return target
