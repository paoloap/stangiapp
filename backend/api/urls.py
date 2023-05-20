from django.urls import include, path
from .views import *
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('user_profile', user_profile, name='user_profile'),
    path('user_reminders', user_reminders, name='user_reminders'),
    path('open_reminder', open_reminder, name='open_reminder'),
    path('login', login_view, name='login'),
    path('refresh_token', refresh_token_view, name='refresh_token'),
    path('change_password', change_password, name='change_password'),
    path('change_reminder_status', change_reminder_status, name='change_reminder_status'),
    path('attach_file', attach_file, name='attach_file'),
    path('delete_attachment', delete_attachment, name='delete_attachment'),
    path('global_attachments', global_attachments, name='global_attachments'),
    path('download_attachment', download_attachment, name='download_attachment'),
    path("password_reset", password_reset_request, name="password_reset"),
    path("logout", logout, name="logout"),
]
