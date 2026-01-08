"""WSGI config for the project.
Exposes the WSGI callable as a module-level variable named `application`.
"""
import os
# os is used to set the default settings module.
from django.core.wsgi import get_wsgi_application
# get_wsgi_application returns a WSGI callable for deployment.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sitefiles.settings')
# Ensure the settings module is set for WSGI servers.

application = get_wsgi_application()
# The WSGI application used by deployment servers to forward requests to Django.
