from django.core.mail import send_mail
from django.conf import settings
from .models import EmailLog
import traceback


def send_email_and_log(subject, body, from_email, recipient_list):
    """Send an email and record the attempt in EmailLog.

    Parameters:
    - subject: Email subject string.
    - body: Email body string.
    - from_email: Sender address (falls back to settings.DEFAULT_FROM_EMAIL).
    - recipient_list: Iterable of recipient email addresses.

    Returns True on success, False on failure. On failure the EmailLog.error field
    will contain the exception message and traceback for easier debugging.
    """
    # Prepare a comma-separated recipients string for the log entry.
    recipients_str = ','.join(recipient_list or [])

    # Create the log record immediately so we have a row to update.
    log = EmailLog.objects.create(
        subject=subject,
        body=body,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        recipients=recipients_str,
    )

    try:
        # Use Django's send_mail; fail_silently=False so we get exceptions to record.
        result = send_mail(subject, body, from_email or settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
        log.sent = bool(result)
        log.save(update_fields=['sent'])
        return True
    except Exception as exc:
        # Record both the exception message and the full traceback for diagnostics.
        tb = traceback.format_exc()
        log.sent = False
        log.error = f"{str(exc)}\n\nTraceback:\n{tb}"
        log.save(update_fields=['sent', 'error'])
        return False
