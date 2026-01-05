#!/usr/bin/env python
# manage.py is the command-line utility for administrative tasks in Django projects.
import os
# os lets us interact with environment variables and the file system.
import sys
# sys gives access to interpreter variables and functions.

if __name__ == '__main__':
    # This ensures the script runs only when executed directly, not when imported.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sitefiles.settings')
    # Set the default settings module for Django to use.
    try:
        from django.core.management import execute_from_command_line
        # Imports the Django helper to run management commands like runserver and migrate.
    except ImportError as exc:
        # If Django isn't installed, inform the user with the original error attached.
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH?"
        ) from exc
    execute_from_command_line(sys.argv)
    # Pass command-line arguments (like runserver) to Django's command runner.
