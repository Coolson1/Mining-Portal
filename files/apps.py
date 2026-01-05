from django.apps import AppConfig
# AppConfig is used to configure some attributes of the app.


class FilesConfig(AppConfig):
    # Name of the app as referenced by Django settings.
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'files'
