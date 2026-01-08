import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sitefiles.settings')
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import django
django.setup()
from django.core.mail import send_mail
from django.conf import settings

print('EMAIL_BACKEND=', settings.EMAIL_BACKEND)
print('DEFAULT_FROM_EMAIL=', settings.DEFAULT_FROM_EMAIL)
try:
    res = send_mail('Test mail from app', 'This is a test.', settings.DEFAULT_FROM_EMAIL, [os.environ.get('TEST_RECIPIENT','abdul1ck2@gmail.com')], fail_silently=False)
    print('send_mail returned:', res)
except Exception as e:
    print('send_mail exception:', e)
