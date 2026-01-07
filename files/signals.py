from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import EmailLog
from .models import FileUpload
from .utils import send_email_and_log

@receiver(post_save, sender=FileUpload)
def file_uploaded_notify(sender, instance, created, **kwargs):
    if not created:
        return
    # Prepare recipients: all active users with an email
    recipients = list(User.objects.filter(is_active=True).exclude(email='').values_list('email', flat=True))
    if not recipients:
        return
    subject = f'New file uploaded: {instance.title}'
    uploaded_by = getattr(instance.uploaded_by, 'username', 'Unknown')
    body = (
        f'Filename: {getattr(instance.file, "name", "")}\n'
        f'Title: {instance.title}\n'
        f'Level: {instance.level}\n'
        f'Category: {instance.category}\n'
        f'Semester: {instance.semester}\n'
        f'Uploaded by: {uploaded_by}\n'
        f'Upload date: {instance.uploaded_at}\n'
    )
    try:
        # Prefer the helper which records detailed errors and tracebacks.
        ok = send_email_and_log(subject, body, settings.DEFAULT_FROM_EMAIL, recipients)
        # If helper returned False it has already recorded the failure in EmailLog.
    except Exception:
        # Avoid raising from signal handler; attempt to record a minimal EmailLog entry.
        try:
            EmailLog.objects.create(subject=subject, body=body, from_email=settings.DEFAULT_FROM_EMAIL, recipients=','.join(recipients), sent=False, error='send failed (exception in signal)')
        except Exception:
            pass
