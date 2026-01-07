import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so `sitefiles` can be imported when run from scripts/
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sitefiles import settings

print('cwd=', Path.cwd())
print('sys.path[0]=', sys.path[0])
print('DEBUG=', settings.DEBUG)
print('EMAIL_BACKEND=', getattr(settings, 'EMAIL_BACKEND', None))
print('GMAIL_HOST_USER=', os.environ.get('GMAIL_HOST_USER'))
print('GMAIL_APP_PASSWORD=', 'SET' if os.environ.get('GMAIL_APP_PASSWORD') else 'NOT SET')
print('EMAIL_HOST_USER=', getattr(settings, 'EMAIL_HOST_USER', None))
print('EMAIL_HOST_PASSWORD=', getattr(settings, 'EMAIL_HOST_PASSWORD', None))
