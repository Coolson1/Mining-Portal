import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sitefiles.settings')
import django
django.setup()
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from files.models import EmailLog

email = None
if len(sys.argv) > 1:
    email = sys.argv[1]
else:
    print('Usage: resend_welcome.py user@example.com')
    sys.exit(2)

try:
    user = User.objects.filter(email__iexact=email).order_by('-id').first()
    if not user:
        print('No user found with email', email)
        sys.exit(1)
    username = user.username
    subject = 'Welsome to our platform'
    body = f'Hello {username}, thank you for registering.'
    sent = False
    try:
        from files.utils import send_email_and_log
        ok = send_email_and_log(subject, body, settings.DEFAULT_FROM_EMAIL, [email])
        sent = bool(ok)
        print('send_email_and_log returned', ok)
    except Exception as e:
        print('send_email_and_log not available or failed:', e)
        try:
            res = send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
            EmailLog.objects.create(subject=subject, body=body, from_email=settings.DEFAULT_FROM_EMAIL, recipients=email, sent=bool(res))
            sent = bool(res)
            print('send_mail returned', res)
        except Exception as ex:
            EmailLog.objects.create(subject=subject, body=body, from_email=settings.DEFAULT_FROM_EMAIL, recipients=email, sent=False, error=str(ex))
            print('send_mail failed:', ex)
    if sent:
        print('Welcome email sent to', email)
    else:
        print('Failed to send welcome email to', email)
except Exception as exc:
    print('Error:', exc)
    sys.exit(3)
