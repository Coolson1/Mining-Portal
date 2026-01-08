from django.core.mail import send_mail
from django.conf import settings
from .models import EmailLog


def send_email_and_log(subject, body, from_email, recipient_list):
    recipients_str = ','.join(recipient_list or [])
    log = EmailLog.objects.create(subject=subject, body=body, from_email=from_email or settings.DEFAULT_FROM_EMAIL, recipients=recipients_str)
    try:
        result = send_mail(subject, body, from_email or settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
        log.sent = bool(result)
        log.save(update_fields=['sent'])
        return True
    except Exception as exc:
        log.sent = False
        log.error = str(exc)
        log.save(update_fields=['sent', 'error'])
        return False
