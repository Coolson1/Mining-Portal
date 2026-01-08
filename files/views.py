from django.shortcuts import render, get_object_or_404, redirect
# render helps render templates; get_object_or_404 fetches objects or returns 404.
from django.http import FileResponse
# FileResponse streams files efficiently for downloads.
import os
# os is used to manipulate file path components (basename, etc.).
import mimetypes
# mimetypes helps guess the correct Content-Type for the downloaded file.
from django.utils.encoding import smart_str
# smart_str helps ensure filenames are encoded safely for HTTP headers.
from .models import FileUpload, CATEGORY_CHOICES, SEMESTER_CHOICES
from .forms import StudentRegistrationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from collections import OrderedDict
from django.utils import timezone
# messages can show feedback to users on registration/login.
import shutil
import datetime


def index(request, level=None, category=None, semester=None):
    # View for the home page that lists uploaded files.
    # If `level` and/or `category` provided, filter files accordingly.
    # Only show non-archived files on the public home page
    files_qs = FileUpload.objects.filter(archived=False).order_by('-uploaded_at')
    # Build a simple level list for the template (1..5) and category list from model choices.
    levels = [1, 2, 3, 4, 5]
    current_level = None
    # Build categories list from model-level choices so template can iterate labels and keys.
    categories = [{'key': k, 'label': v} for k, v in CATEGORY_CHOICES]
    current_category = None
    # Semesters for the template
    semesters = [{'key': k, 'label': v} for k, v in SEMESTER_CHOICES]
    current_semester = None

    # Apply level filter if provided and valid.
    if level:
        try:
            level_int = int(level)
            if level_int in levels:
                files_qs = files_qs.filter(level=level_int)
                current_level = level_int
        except (TypeError, ValueError):
            current_level = None

    # Apply category filter if provided and valid.
    if category:
        # Accept either the key (notes, past_papers, assignments) or a display label.
        valid_keys = [k for k, _ in CATEGORY_CHOICES]
        if category in valid_keys:
            files_qs = files_qs.filter(category=category)
            current_category = category

    # Apply semester filter if provided
    if semester:
        try:
            sem_int = int(semester)
            valid_semesters = [k for k, _ in SEMESTER_CHOICES]
            if sem_int in valid_semesters:
                files_qs = files_qs.filter(semester=sem_int)
                current_semester = sem_int
        except (TypeError, ValueError):
            current_semester = None

    # followed by the files uploaded on that date. Make handling robust
    # for naive vs aware datetimes so uploads on different dates separate correctly.
    groups = OrderedDict()
    for f in files_qs:
        dt = f.uploaded_at
        try:
            if timezone.is_naive(dt):
                aware = timezone.make_aware(dt, timezone.get_default_timezone())
            else:
                aware = dt
            d = timezone.localtime(aware).date()
        except Exception:
            try:
                d = dt.date()
            except Exception:
                d = None
        key = d.strftime('%Y-%m-%d') if d is not None else f'unknown-{f.pk}'
        groups.setdefault(key, []).append(f)

    # Sort files in each date group alphabetically by first letter (case-insensitive),
    # then by full title to stabilize ordering.
    for k, lst in groups.items():
        lst.sort(key=lambda obj: (((obj.title or '')[:1] or '').lower(), (obj.title or '').lower()))
    # Check for likely OneDrive-synced project folder which can overwrite db.sqlite3
    # and cause 'missing user' issues when files are synced across devices.
    db_path = settings.DATABASES.get('default', {}).get('NAME', '')
    if isinstance(db_path, str) and 'onedrive' in db_path.lower():
        messages.warning(request, 'Warning: project appears inside OneDrive. Database file may be overwritten by sync; consider moving the project or the DB to a stable location.')

    return render(request, 'files/index.html', {
        'files_groups': groups,
        'levels': levels,
        'current_level': current_level,
        'semesters': semesters,
        'current_semester': current_semester,
        'categories': categories,
        'current_category': current_category,
    })
    # Render the template with files, available levels/categories, and current selections.


def download_file(request, pk):
    # View to download a file by its primary key (id).
    obj = get_object_or_404(FileUpload, pk=pk)
    # Fetch the object or return a 404 response if not found.

    # Use only the base filename (no directory components) for the download filename.
    filename = os.path.basename(obj.file.name)
    # Guess the MIME type (content type) from the filename extension.
    content_type, encoding = mimetypes.guess_type(filename)
    if not content_type:
        # Fall back to a generic binary stream if unknown.
        content_type = 'application/octet-stream'

    # Open the underlying file in binary mode for streaming.
    file_handle = obj.file.open('rb')

    # Increment download counter (best-effort) before returning response.
    try:
        obj.increment_downloads()
    except Exception:
        pass

    # Create a FileResponse with the guessed content type and a clean filename.
    # `as_attachment=True` instructs browsers to download rather than display inline.
    response = FileResponse(file_handle, as_attachment=True, filename=smart_str(filename), content_type=content_type)

    # Some clients may need an explicit Content-Disposition header; FileResponse sets one,
    # but we ensure the header uses a safe, encoded filename.
    response['Content-Disposition'] = f'attachment; filename="{smart_str(filename)}"'

    return response


def register(request):
    # Registration view: create User + StudentProfile then redirect to login.
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            # Make a quick DB backup after a new registration to reduce risk of OneDrive overwrites
            try:
                db_path = settings.DATABASES.get('default', {}).get('NAME')
                if db_path:
                    db_file = str(db_path)
                    if os.path.exists(db_file):
                        backups_dir = os.path.join(settings.BASE_DIR, 'db_backups')
                        os.makedirs(backups_dir, exist_ok=True)
                        ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
                        shutil.copy2(db_file, os.path.join(backups_dir, f'db_backup_{ts}.sqlite3'))
            except Exception:
                pass

            # Do not send emails on registration and avoid showing email-sent alerts.
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('files:login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    # Simple login view that authenticates by username and password.
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # On successful login, create a lightweight DB backup to reduce data loss
            try:
                db_path = settings.DATABASES.get('default', {}).get('NAME')
                if db_path:
                    db_file = str(db_path)
                    if os.path.exists(db_file):
                        backups_dir = os.path.join(settings.BASE_DIR, 'db_backups')
                        os.makedirs(backups_dir, exist_ok=True)
                        ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
                        shutil.copy2(db_file, os.path.join(backups_dir, f'db_login_backup_{ts}.sqlite3'))
            except Exception:
                pass
            login(request, user)
            return redirect('files:home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'registration/login.html')


# Protect the main pages so only authenticated students can view and download files.
index = login_required(index)
download_file = login_required(download_file)


def preview_file(request, pk):
    # Stream the file with an inline Content-Disposition so browsers can render it.
    obj = get_object_or_404(FileUpload, pk=pk)
    filename = os.path.basename(obj.file.name)
    content_type, encoding = mimetypes.guess_type(filename)
    if not content_type:
        content_type = 'application/octet-stream'

    file_handle = obj.file.open('rb')
    response = FileResponse(file_handle, content_type=content_type)
    response['Content-Disposition'] = f'inline; filename="{smart_str(filename)}"'
    # Allow same-origin embedding for previews (development only).
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


preview_file = login_required(preview_file)


def preview_page(request, pk):
    # Render a small page that embeds the media file URL in an iframe.
    obj = get_object_or_404(FileUpload, pk=pk)
    # Use the storage-provided URL so the browser can load it directly.
    file_url = obj.file.url
    preview_view_url = reverse('files:preview', args=[pk])
    # Try to guess a MIME type for rendering decisions in the template.
    content_type, encoding = mimetypes.guess_type(obj.file.name)
    if not content_type:
        content_type = 'application/octet-stream'
    # Precompute simple flags so template logic stays simple and valid.
    is_image = content_type.startswith('image')
    is_pdf = 'pdf' in content_type
    is_text = content_type.startswith('text')
    return render(request, 'files/preview_page.html', {
        'file': obj,
        'file_url': file_url,
        'preview_view_url': preview_view_url,
        'content_type': content_type,
        'is_image': is_image,
        'is_pdf': is_pdf,
        'is_text': is_text,
    })


preview_page = login_required(preview_page)
