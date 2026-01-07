from django.apps import AppConfig
# AppConfig is used to configure some attributes of the app.


class FilesConfig(AppConfig):
    # Name of the app as referenced by Django settings.
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'files'
    def ready(self):
        # Import signals to ensure receivers are connected when app is ready.
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
