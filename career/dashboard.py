"""Local dashboard. All content is escaped; POST requires an unguessable form token."""
import asyncio
import html
import json
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlsplit, urlunsplit
from .store import Store, digest
from .agent import generate, TASKS
from .urls import canonical_url

def serve(config, port=8421):
    csrf = secrets.token_urlsafe(24)
    def esc(s): return html.escape(str(s), quote=True)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass
        def send(self, content, status=200, mime='text/html; charset=utf-8'):
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(content.encode())
        def host_ok(self):
            return self.headers.get('Host') in {f'localhost:{port}',f'127.0.0.1:{port}'}
        def do_GET(self):
            if not self.host_ok(): return self.send('Invalid host',403)
            if self.path == '/health': return self.send('{"status":"ok"}',mime='application/json')
            if self.path != '/': return self.send('Not found',404)
            store = Store()
            try:
                rows = store.records()
                runs = [dict(r) for r in store.db.execute('SELECT * FROM runs ORDER BY id DESC LIMIT 30')]
                hidden = f'<input type="hidden" name="csrf" value="{csrf}">'
                def form(action, body): return f'<form method="post" action="{action}">{hidden}{body}</form>'
                cards = ''
                for r in rows:
                    if r['kind'] == 'history': continue
                    options = ''.join(f'<option>{x}</option>' for x in ['approved','rejected','completed','applied','responded','interview','offer','accepted','declined'])
                    controls = form('/status',f'<input type="hidden" name="id" value="{esc(r["id"])}"><select name="status">{options}</select><button>Record status</button>')
                    cards += f'<article><h3>{esc(r["title"])}</h3><p class="tag">{esc(r["kind"])} · {esc(r["status"])}</p><details><summary>Read record</summary><pre>{esc(r["body"])}</pre></details>{controls}</article>'
                total = sum((r['input_tokens'] or 0)+(r['output_tokens'] or 0) for r in runs)
                page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>PJ Career Assistant</title>
                <style>body{font:16px system-ui;background:#f4f5f0;color:#16352c;max-width:1050px;margin:40px auto;padding:20px}h1{font-size:38px}article,section{background:white;border-radius:14px;padding:24px;margin:16px 0;border:1px solid #dae1d8}textarea{box-sizing:border-box;width:100%;min-height:120px}input,textarea,select,button{font:inherit;padding:10px;margin:6px 0;border:1px solid #b4c6ba;border-radius:6px}button{background:#164a3d;color:white;cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px system-ui}.tag{color:#577260}small{color:#53635b}</style>
                <h1>PJ Career Assistant</h1><p>One workspace for your next career step.</p>'''
                page += f'<p>{len(rows)} records · {total:,} tokens in last 30 runs · daily limit {config.daily_calls} API attempts</p>'
                page += '<p>UK · UAE / Dubai · Oman · Qatar · Kuwait</p><p>Draft and review only. Status changes record your manual actions; nothing is sent or published.</p>'
                page += f'<p>API status: {esc(store.setting("api_blocked") or "ready; credit not guaranteed")}</p>'
                page += '<section><h2>Your evidence</h2><p>Paste your CV and country-specific work authorisation. Saved locally and included in requested AI tasks.</p>'+form('/profile',f'<textarea name="profile" maxlength="16000">{esc(store.setting("profile"))}</textarea><button>Save profile</button>')+'</section>'
                page += '<section><h2>Create a draft</h2>'+form('/generate','<select name="task">'+''.join(f'<option>{x}</option>' for x in TASKS)+'</select><textarea name="request" maxlength="12000" required placeholder="Topic, verified recruiter profile or vacancy text. Include today’s date for a fresh job search."></textarea><button>Generate once</button><p><small>Identical requests reuse saved output. Web search fees are not included in token-only cost estimates.</small></p>')+'</section>'
                page += '<section><h2>Track an application or response</h2>'+form('/application','<input name="url" required type="url" placeholder="Employer vacancy URL"><input name="title" required placeholder="Employer — role"><textarea name="body" placeholder="Notes and response history"></textarea><button>Save application record</button>')+'</section>'
                page += '<h2>Your work</h2>'+cards
                page += '<section><h2>Run history</h2><pre>'+esc(json.dumps([{k:r[k] for k in ('id','task','status','input_tokens','output_tokens','cost','error','created')} for r in runs],indent=2))+'</pre></section>'
                self.send(page+'</html>')
            finally: store.close()
        def do_POST(self):
            if not self.host_ok(): return self.send('Invalid host',403)
            try:
                n = int(self.headers.get('Content-Length','0'))
                if not 0 < n <= 100000: return self.send('Invalid request size',413)
                data = {k:v[0] for k,v in parse_qs(self.rfile.read(n).decode(),keep_blank_values=True).items()}
                if not secrets.compare_digest(data.get('csrf',''),csrf): return self.send('Invalid form token',403)
                store = Store()
                try:
                    if self.path == '/profile':
                        if len(data['profile'])>16000: raise ValueError('Profile too long')
                        store.set_setting('profile',data['profile'])
                    elif self.path == '/generate': asyncio.run(generate(store,config,data['task'],data['request']))
                    elif self.path == '/status': store.transition(data['id'],data['status'])
                    elif self.path == '/application':
                        url = canonical_url(data['url'])
                        id = 'application:'+digest(url)
                        existing = store.get(id)
                        store.put(id,'application',data['title'],existing['status'] if existing else 'saved',data['body'],url)
                    else: raise ValueError('Unknown action')
                finally: store.close()
                self.send_response(303); self.send_header('Location','/'); self.end_headers()
            except (ValueError,KeyError):
                self.send('Action could not complete. Check input and run history. <a href="/">Return</a>',400)
    server = HTTPServer(('127.0.0.1',port),Handler)
    print(f'PJ Career Assistant: http://127.0.0.1:{port}',flush=True)
    try: server.serve_forever()
    finally: server.server_close()
