from django.contrib import admin
# admin lets us register models to appear in the Django admin site.
from .models import FileUpload
# Import the model defined in this app so we can register it.


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    # Admin configuration for the FileUpload model.
    # Columns to display in the admin list view for uploaded files.
    list_display = ('title', 'level', 'category', 'uploaded_at', 'download_count')
    # Allow filtering by level and category in the right sidebar of the admin changelist.
    list_filter = ('level', 'category')
    # Enable simple search by title in the admin list view.
    search_fields = ('title',)
