import asyncio
from pathlib import Path
import tempfile
import unittest
from career.store import Store
from career.config import Config
from career.agent import generate
from career.agent import error_code
from career.migrate import migrate

class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.tmp.name)/'state.sqlite')
        self.config = Config(daily_calls=2)
        self.calls = 0
    def tearDown(self): self.store.close(); self.tmp.cleanup()
    async def runner(self,*args):
        self.calls += 1
        return 'A useful draft',(100,40)
    def run_task(self,task='linkedin',request='A distinct topic',runner=None):
        return asyncio.run(generate(self.store,self.config,task,request,runner or self.runner))
    def test_repeat_uses_no_model_call(self):
        first = self.run_task(); second = self.run_task()
        self.assertFalse(first['cached']); self.assertTrue(second['cached']); self.assertEqual(self.calls,1)
        self.assertEqual(len(self.store.records('draft')),1)
    def test_cap_and_cached_access(self):
        self.run_task(request='one'); self.run_task(request='two')
        with self.assertRaisesRegex(ValueError,'limit'): self.run_task(request='three')
        self.assertTrue(self.run_task(request='one')['cached'])
    def test_profile_change_invalidates_cache(self):
        self.run_task(); self.store.set_setting('profile','New verified profile'); self.run_task()
        self.assertEqual(self.calls,2)
    def test_no_fit_without_profile(self):
        with self.assertRaisesRegex(ValueError,'CV/profile'): self.run_task('fit')
        self.assertEqual(self.calls,0)
    def test_quota_circuit_and_no_secret_logging(self):
        class Quota(Exception): code='insufficient_quota'
        async def fail(*args): raise Quota('SECRET must not be stored')
        with self.assertRaisesRegex(ValueError,'insufficient_quota'): self.run_task(runner=fail)
        with self.assertRaisesRegex(ValueError,'paused'): self.run_task(request='new')
        log = str([tuple(r) for r in self.store.db.execute('SELECT * FROM runs')])
        self.assertNotIn('SECRET',log)
    def test_concurrent_reservation_blocks_second(self):
        self.store.reserve('first','linkedin',2)
        other = Store(self.store.path)
        try:
            with self.assertRaisesRegex(ValueError,'progress'): other.reserve('second','jobs',2)
        finally: other.close()
    def test_review_cannot_skip_approval(self):
        self.store.put('x','draft','Example','draft','Content')
        with self.assertRaises(ValueError): self.store.transition('x','completed')
        self.store.transition('x','approved'); self.store.transition('x','completed')
        with self.assertRaises(ValueError): self.store.transition('x','approved')
    def test_import_is_idempotent_and_new_post_status_wins(self):
        p=Path(self.tmp.name)
        (p/'linkedin-post-today.md').write_text('Status: PUBLISHED\nPost text')
        (p/'linkedin-networking-log.md').write_text('Morning post remains a draft')
        self.assertEqual(migrate(self.store,p),2)
        self.assertEqual(migrate(self.store,p),0)
        self.assertEqual(self.store.get('post:linkedin-post-today')['status'],'published')
    def test_timeout_not_retried(self):
        class APITimeoutError(Exception): pass
        async def fail(*args):
            self.calls += 1
            raise APITimeoutError()
        with self.assertRaisesRegex(ValueError,'timeout'): self.run_task(runner=fail)
        self.assertEqual(self.calls,1)
    def test_string_error_body_does_not_break_recovery(self):
        class Broken(Exception): body={'error':'not an object'}
        self.assertEqual(error_code(Broken()),'api_failure')
    def test_daily_does_not_regenerate_imported_post(self):
        from career.daily import daily
        from unittest.mock import patch
        from datetime import datetime
        from zoneinfo import ZoneInfo
        self.store.put('post:linkedin-post-2026-09-08-pm','post','Today','published','Existing')
        class Clock:
            @staticmethod
            def now(tz): return datetime(2026,9,8,17,0,tzinfo=ZoneInfo('Europe/London'))
        with patch('career.daily.datetime',Clock):
            result=asyncio.run(daily(self.store,self.config))
        self.assertIn('skipped',result[0])
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM runs').fetchone()[0],0)
    def test_daily_slot_survives_profile_change(self):
        from career.daily import daily
        from unittest.mock import patch, AsyncMock
        from datetime import datetime
        from zoneinfo import ZoneInfo
        class Clock:
            @staticmethod
            def now(tz): return datetime(2026,9,8,17,0,tzinfo=ZoneInfo('Europe/London'))
        fake=AsyncMock(return_value={'id':'draft:example','cached':False})
        with patch('career.daily.datetime',Clock),patch('career.daily.generate',fake):
            asyncio.run(daily(self.store,self.config))
            self.store.set_setting('profile','Updated CV')
            second=asyncio.run(daily(self.store,self.config))
        self.assertEqual(fake.await_count,1)
        self.assertIn('skipped',second[0])
    def test_application_url_ignores_tracking_but_preserves_job_id(self):
        from career.urls import canonical_url
        self.assertEqual(canonical_url('https://EXAMPLE.com/jobs/?jobId=4&utm_source=linkedin#top'),
                         canonical_url('https://example.com/jobs?jobId=4'))
        self.assertNotEqual(canonical_url('https://example.com/jobs?jobId=4'),canonical_url('https://example.com/jobs?jobId=5'))

if __name__ == '__main__': unittest.main()
