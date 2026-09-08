import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

class PublicDemoTests(unittest.TestCase):
    def test_demo_runs_without_site_packages(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'demo.html'
            subprocess.run([sys.executable,'-S',str(ROOT/'demo.py'),'--output',str(output)],check=True,capture_output=True)
            text=output.read_text()
            self.assertIn('OFFLINE DEMO',text)
            self.assertIn('Fictional sample data',text)
            self.assertNotIn('<script',text)
    def test_demo_does_not_import_api_or_application_state(self):
        spec=importlib.util.spec_from_file_location('public_demo',ROOT/'demo.py')
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        self.assertNotIn('OPENAI_API_KEY',module.render())
        self.assertIn('Zero API calls',module.render())
