import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from career.store import Store
from career.config import Config
from career.dashboard import serve

class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=Path(self.tmp.name)/'state.sqlite'
        self.handler=None
        class Server:
            def __init__(inner,address,handler): self.handler=handler
            def serve_forever(inner): pass
            def server_close(inner): pass
        with patch('career.dashboard.HTTPServer',Server): serve(Config())
        self.store_patch=patch('career.dashboard.Store',lambda: Store(self.db))
        self.store_patch.start()
    def tearDown(self): self.store_patch.stop(); self.tmp.cleanup()
    def request(self,path='/',method='GET',host='127.0.0.1:8421',body=b''):
        h=self.handler.__new__(self.handler)
        h.path=path
        h.headers={'Host':host,'Content-Length':str(len(body))}
        h.wfile=io.BytesIO(); h.rfile=io.BytesIO(body)
        result={'status':None,'headers':{}}
        h.send_response=lambda x: result.update(status=x)
        h.send_header=lambda k,v: result['headers'].update({k:v})
        h.end_headers=lambda:None
        getattr(h,'do_'+method)()
        result['body']=h.wfile.getvalue().decode()
        return result
    def test_dashboard_escapes_untrusted_records(self):
        s=Store(self.db); s.put('x','draft','<script>alert(1)</script>','draft','<img onerror="bad">'); s.close()
        r=self.request()
        self.assertEqual(r['status'],200)
        self.assertNotIn('<script>',r['body'])
        self.assertIn('&lt;script&gt;',r['body'])
        self.assertIn("frame-ancestors 'none'",r['headers']['Content-Security-Policy'])
    def test_cross_site_post_rejected(self):
        self.assertEqual(self.request('/profile','POST',body=b'profile=malicious')['status'],403)
        s=Store(self.db); self.assertEqual(s.setting('profile'),''); s.close()
    def test_dns_rebinding_host_rejected(self):
        self.assertEqual(self.request(host='attacker.example')['status'],403)
    def test_health(self):
        r=self.request('/health'); self.assertEqual(r['status'],200)
        self.assertEqual(r['body'],'{"status":"ok"}')
