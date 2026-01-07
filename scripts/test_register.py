import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sitefiles.settings')
import sys
# Ensure project root is on sys.path before importing Django so settings import works
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import django
django.setup()
from django.test import Client
from django.contrib.auth.models import User

# Ensure test username is unique
username = 'testuser_for_email'
if User.objects.filter(username=username).exists():
    User.objects.filter(username=username).delete()

c = Client()
data = {
    'username': username,
    'first_name': 'Test',
    'middle_name': 'T',
    'last_name': 'User',
    'email': os.environ.get('TEST_RECIPIENT', 'abdul1ck2@gmail.com'),
    'level': '1',
    'password1': 'Testpass123',
    'password2': 'Testpass123',
}
print('Posting registration for', username)
resp = c.post('/register/', data)
print('Response status:', resp.status_code)
if hasattr(resp, 'redirect_chain'):
    print('Redirect chain:', resp.redirect_chain)
else:
    print('Response headers:', dict(resp.items()))
print('Response cookies:', resp.cookies)

# Check that user created
from django.contrib.auth.models import User
u = User.objects.filter(username=username).first()
print('User created:', bool(u))
if u:
    print('User email:', u.email)
else:
    print('User not created. Form errors may have occurred.')

print('Done')
