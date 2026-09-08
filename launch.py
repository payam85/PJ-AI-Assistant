"""Portable launcher; machine-specific references stay in ignored private storage."""
import json
import os
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
config_file = root / 'private' / 'runtime.json'
config = json.loads(config_file.read_text()) if config_file.exists() else {}
local_python = root / '.venv' / 'bin' / 'python'
python = config.get('python') or (str(local_python) if local_python.exists() else sys.executable)
env = dict(os.environ)
if config.get('env_file'):
    env.setdefault('PJ_ENV_FILE', config['env_file'])
os.execve(python, [python, str(root / 'app.py'), *sys.argv[1:]], env)
