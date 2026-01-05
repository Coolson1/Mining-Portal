from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns # new
# path is used to map URL patterns to view callables.
from . import views
# Import views from the current app to connect them to URLs.

app_name = 'files'
# Namespace for URL reversing (not strictly required but helpful).

urlpatterns = [
    # Root serves the registration page so visitors see the register form first.
    path('', views.register, name='root_register'),
    # Home page listing files (requires login) is available at /home/ and kept
    # under the name 'home' so existing redirects continue to work.
    path('home/', views.index, name='home'),
    path('level/<int:level>/', views.index, name='level'),
    # Home page filtered by level (1-5).
    path('category/<slug:category>/', views.index, name='category'),
    # Home page filtered by category (notes, past_papers, assignments).
    path('download/<int:pk>/', views.download_file, name='download'),
    path('preview/<int:pk>/', views.preview_file, name='preview'),
    path('preview-page/<int:pk>/', views.preview_page, name='preview_page'),
    # Download URL for a specific file by its primary key.
    path('register/', views.register, name='register'),
    # Student registration page (also available at root).
    path('login/', views.login_view, name='login'),
    # Student login page.
]

urlpatterns += staticfiles_urlpatterns() # new