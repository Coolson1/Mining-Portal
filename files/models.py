from django.db import models
import os
# Import Django's model base and field types.
from django.contrib.auth.models import User
# Import the built-in User model to attach a student profile.


# Reusable level choices (module-level so multiple models can reference them).
LEVEL_CHOICES = [
    (1, 'Level 1'),
    (2, 'Level 2'),
    (3, 'Level 3'),
    (4, 'Level 4'),
    (5, 'Level 5'),
]

# Reusable category choices for uploaded files.
CATEGORY_CHOICES = [
    ('notes', 'Notes'),
    ('past_papers', 'Past Papers'),
    ('assignments', 'Assignments'),
]


class FileUpload(models.Model):
    # Model representing an uploaded file with a title, level, category and timestamp.
    title = models.CharField(max_length=255)
    # Short text field to store the file's display title.
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=1)
    # PositiveSmallIntegerField stores small integers; choices restrict values to 1-5.
    file = models.FileField(upload_to='uploads/')
    # FileField stores the uploaded file and saves it under MEDIA_ROOT/uploads/.
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='notes')
    # CharField with choices to restrict category values and display readable labels.
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Timestamp automatically set when the object is first created.
    download_count = models.PositiveIntegerField(default=0)
    # Track how many times this file has been downloaded.

    def __str__(self):
        # Human-readable display of the object, used in admin listings.
        return f"{self.title} - Level {self.level} ({self.uploaded_at:%Y-%m-%d %H:%M})"

    @property
    def file_type(self):
        """Return the file extension (e.g. 'pdf', 'jpg') in lowercase without the dot."""
        try:
            return os.path.splitext(self.file.name)[1].lstrip('.').lower()
        except Exception:
            return ''

    @property
    def file_size(self):
        """Return the file size in bytes (0 if unavailable)."""
        try:
            return self.file.size or 0
        except Exception:
            return 0

    @property
    def file_size_display(self):
        """Return a human-readable file size string (KB/MB)."""
        size = self.file_size
        # simple human readable conversion
        for unit in ['bytes', 'KB', 'MB', 'GB']:
            if size < 1024 or unit == 'GB':
                if unit == 'bytes':
                    return f"{size} {unit}"
                return f"{size:.1f} {unit}"
            size = size / 1024.0
        return f"{self.file_size} bytes"

    def increment_downloads(self):
        """Increment download_count safely and save the model."""
        try:
            self.download_count = (self.download_count or 0) + 1
            # Use update to avoid race when multiple downloads occur.
            type(self).objects.filter(pk=self.pk).update(download_count=self.download_count)
        except Exception:
            # Fallback: attempt a normal save
            try:
                self.save(update_fields=['download_count'])
            except Exception:
                pass


class StudentProfile(models.Model):
    # Profile model to store additional student info linked to Django's User.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Middle name is optional per your request.
    middle_name = models.CharField(max_length=150, blank=True)
    # Level should match the FileUpload levels (1-5).
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=1)

    def __str__(self):
        # Display the username and level for easy admin reading.
        return f"{self.user.username} - Level {self.level}"
