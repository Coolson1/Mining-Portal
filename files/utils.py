"""Email sending utilities used across the project.

This module exposes `send_email_and_log` which attempts to deliver email
using the configured Django email backend and records the attempt in the
`EmailLog` model. It also includes an optional SendGrid HTTP fallback when
`SENDGRID_API_KEY` is provided in the environment.

The function:
 - creates an `EmailLog` entry immediately so every attempt is recorded,
 - opens a mail connection (so SMTP debuglevel can be enabled via env var),
 - records full exception tracebacks in `EmailLog.error`, and
 - optionally falls back to SendGrid for delivery if configured.

Comments are included to aid future debugging and to explain behavior.
"""

from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from .models import EmailLog
import traceback
import os
import json

try:
    import requests  # optional; only used for SendGrid fallback
except Exception:
    requests = None


def _send_via_sendgrid(subject, body, from_email, recipient_list):
    """Send the message using the SendGrid Web API.

    Returns True on success, False otherwise. Requires `requests` and the
    `SENDGRID_API_KEY` environment variable to be set.
    """
    api_key = os.environ.get('SENDGRID_API_KEY')
    if not api_key or not requests:
        return False

    url = 'https://api.sendgrid.com/v3/mail/send'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    data = {
        'personalizations': [{'to': [{'email': r} for r in recipient_list]}],
        'from': {'email': from_email},
        'subject': subject,
        'content': [{'type': 'text/plain', 'value': body}],
    }
    try:
        resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
        return resp.status_code in (200, 202)
    except Exception:
        return False


def send_email_and_log(subject, body, from_email, recipient_list):
    """Send an email and record the attempt in EmailLog.

    - `subject`, `body`, `from_email`, `recipient_list` follow Django's
      conventions (strings and iterable of recipient emails).
    - Returns True on success (SMTP or SendGrid), False on failure.

    The function always creates an `EmailLog` row immediately so that every
    send attempt is visible in admin even if delivery later fails.
    """
    # Prepare recipients string for the log record.
    recipients_str = ','.join(recipient_list or [])

    # Create the EmailLog row now so we always have an entry to update.
    log = EmailLog.objects.create(
        subject=subject,
        body=body,
        from_email=from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', ''),
        recipients=recipients_str,
    )

    # Attempt to send using Django's configured email backend via a connection.
    try:
        connection = get_connection(fail_silently=False)

        # Try to open connection to access underlying SMTP object for debuglevel.
        try:
            connection.open()
            smtp_obj = getattr(connection, 'connection', None)
            if smtp_obj and hasattr(smtp_obj, 'set_debuglevel'):
                try:
                    # Enable verbose SMTP logging if SMTP_DEBUG_LEVEL=1 in env.
                    smtp_obj.set_debuglevel(int(os.environ.get('SMTP_DEBUG_LEVEL', '0')))
                except Exception:
                    # Ignore debuglevel setting errors.
                    pass
        except Exception:
            # If explicit open() fails, send_messages will still try to open.
            pass

        # Build and send the message using the connection.
        msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', ''),
            to=list(recipient_list or []),
            connection=connection,
        )
        sent_count = connection.send_messages([msg])

        # Update log with result.
        log.sent = bool(sent_count)
        log.save(update_fields=['sent'])

        if sent_count:
            return True

    except Exception as exc:
        # Record the exception and full traceback in the EmailLog for diagnostics.
        tb = traceback.format_exc()
        try:
            log.sent = False
            log.error = f"SMTP send error: {str(exc)}\n\nTraceback:\n{tb}"
            log.save(update_fields=['sent', 'error'])
        except Exception:
            pass

    # If SMTP didn't send (zero recipients) or failed, optionally try SendGrid.
    try:
        if os.environ.get('SENDGRID_API_KEY'):
            ok = _send_via_sendgrid(subject, body, from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', ''), recipient_list)
            if ok:
                try:
                    log.sent = True
                    log.error = (log.error or '') + '\nFallback: sent via SendGrid.'
                    log.save(update_fields=['sent', 'error'])
                except Exception:
                    pass
                return True
    except Exception:
        try:
            log.error = (log.error or '') + '\nSendGrid fallback failed: ' + traceback.format_exc()
            log.save(update_fields=['error'])
        except Exception:
            pass

    return False
