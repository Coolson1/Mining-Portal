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

    """Email sending utilities used across the project.

    This module exposes `send_email_and_log` which attempts to deliver email
    using the configured Django email backend and records the attempt in the
    `EmailLog` model. It also exposes a SendGrid HTTP fallback if
    `SENDGRID_API_KEY` is set in the environment.

    Why this change: some hosting providers (or SMTP relays) accept messages but
    do not deliver them to the recipient. To help diagnose that situation we:
     - send via a `get_connection()` so we can enable SMTP debuglevel (the raw
       SMTP conversation will appear in process logs),
     - record full exception tracebacks in `EmailLog.error`, and
     - optionally fall back to SendGrid API if configured.
    """

    from django.core.mail import EmailMessage, get_connection
    from django.conf import settings
    from .models import EmailLog
    import traceback
    import os
    import json

    try:
        # requests is not mandatory for SMTP operation; only used if SendGrid is used.
        import requests
    except Exception:
        requests = None


    def _send_via_sendgrid(subject, body, from_email, recipient_list):
        """Send the message using SendGrid Web API if `SENDGRID_API_KEY` present.

        Returns True on success, False otherwise. Requires `requests` and
        `SENDGRID_API_KEY` env var to be set.
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

        The function attempts to deliver using the Django configured backend.
        It opens a connection so that SMTP debuglevel can be enabled (the raw
        SMTP dialogue will be printed to stdout/stderr and appear in hosting logs).

        On failure the EmailLog.error field contains the exception and traceback.
        If SendGrid is configured and the SMTP send fails, we attempt SendGrid as
        a fallback.
        """
        recipients_str = ','.join(recipient_list or [])
        log = EmailLog.objects.create(subject=subject, body=body, from_email=from_email or settings.DEFAULT_FROM_EMAIL, recipients=recipients_str)

        # Attempt to send using Django connection to allow enabling SMTP debuglevel.
        try:
            connection = get_connection(fail_silently=False)
            # Open the connection explicitly so we can access the underlying
            # smtplib.SMTP object and enable debug output (helpful for diagnosing
            # delivery problems; output goes to process logs).
            try:
                connection.open()
                smtp_obj = getattr(connection, 'connection', None)
                if smtp_obj and hasattr(smtp_obj, 'set_debuglevel'):
                    try:
                        # Very verbose SMTP logging (0/1). Set to 1 to enable.
                        smtp_obj.set_debuglevel(int(os.environ.get('SMTP_DEBUG_LEVEL', '0')))
                    except Exception:
                        pass
            except Exception:
                # If opening the connection fails here we'll still try send_messages
                # which will attempt to open it again.
                pass

            msg = EmailMessage(subject=subject, body=body, from_email=from_email or settings.DEFAULT_FROM_EMAIL, to=list(recipient_list or []), connection=connection)
            sent_count = connection.send_messages([msg])
            log.sent = bool(sent_count)
            log.save(update_fields=['sent'])
            # If sent_count is falsy, fall through to potential SendGrid fallback below.
            if sent_count:
                return True
        except Exception as exc:
            tb = traceback.format_exc()
            log.sent = False
            log.error = f"SMTP send error: {str(exc)}\n\nTraceback:\n{tb}"
            log.save(update_fields=['sent', 'error'])

        # SMTP either returned 0 recipients or raised an exception. Try SendGrid
        # fallback if available (this improves deliverability for many hosting
        # platforms and provides a different delivery path).
        try:
            if os.environ.get('SENDGRID_API_KEY'):
                ok = _send_via_sendgrid(subject, body, from_email or settings.DEFAULT_FROM_EMAIL, recipient_list)
                if ok:
                    # Record the success via SendGrid
                    log.sent = True
                    log.error = (log.error or '') + '\nFallback: sent via SendGrid.'
                    log.save(update_fields=['sent', 'error'])
                    return True
        except Exception:
            # ignore SendGrid exceptions but record them
            try:
                log.error = (log.error or '') + '\nSendGrid fallback failed: ' + traceback.format_exc()
                log.save(update_fields=['error'])
            except Exception:
                pass

        return False
