from django.urls import path

from .views import *


urlpatterns = [
    #path('signup/', SignUpView.as_view(), name='signup'),
    path('', home, name='manager.home'),
    path('login/', login, name='manager.login'),
    path('logout/', logout, name='manager.logout'),
    path('crea_utente', create_user_profile, name='manager.create_user_profile'),
    path('elenco_utenti/', list_user_profiles, name='manager.list_user_profiles'),
    path('modifica_utente', manage_user_profile, name='manager.manage_user_profile'),
    path('crea_scadenza', create_reminder, name='manager.create_reminder'),
    path('scadenze_utente', list_user_reminders, name='manager.list_user_reminders'),
    path('modifica_scadenza', edit_reminder, name='manager.edit_reminder'),
]
