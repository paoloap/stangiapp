# from django.contrib.auth.forms import UserCreationForm
# from django.urls import reverse_lazy
# from django.views import generic
from .forms import *
from django.conf import settings

from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.forms import AuthenticationForm
# from django.shortcuts import render_to_response
# from django.template import RequestContext
# from django.utils.http import is_safe_url, urlsafe_base64_decode
# from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect

from api.models import *
from django.contrib.auth import get_user_model

from api.logic import generate_default_db_data
#from geopy.geocoders import Nominatim
#from functools import partial
import re

@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request):
    generate_default_db_data()
    logged_not_manager = False
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            u = form.get_user()
            auth_login(request, u)
            if u.is_staff:
                return HttpResponseRedirect('/manager/')
            else:
                logged_not_manager = True
    else:
        form = AuthenticationForm(request)

    current_site = get_current_site(request)
    context = {
        'form': form,
        'site': current_site,
        'site_name': current_site.name,
        'logged_not_manager': logged_not_manager,
    }
    return TemplateResponse(request, 'manager/login.html', context)

@login_required
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/manager/login')

@login_required
def home(request):
    return TemplateResponse(request, 'manager/home.html')
    
@login_required
def create_reminder(request):
    if request.method == "POST":
        form = ReminderForm(request.POST)
        if form.is_valid():
            new_reminder = form.save()
    else:
        form = ReminderForm()
    current_site = get_current_site(request)
    context = {
        'form': form,
        'site': current_site,
        'site_name': current_site.name,
    }
    return TemplateResponse(request, 'manager/create_reminder.html', context)

@login_required
def create_user_profile(request):
    if 'message' in request.GET:
        message = request.GET['message'].replace("+", " ")
    else:
        message = ""
    is_post = request.method == 'POST'
    post_data = (is_post and request.POST) or None
    user_form = UserForm(post_data)
    user = (is_post and user_form.save()) or None
    context = {'user_form': user_form, 'fields': []}
    fields = get_user_profile_forms(user, post_data)
    context['fields'] = fields
    context['message'] = (is_post and "Utente creato con successo") or message
    return TemplateResponse(request, 'manager/create_user_profile.html', context=context)

@login_required
def list_user_profiles(request):
    users = get_user_model().objects.filter(is_staff=False)
    return TemplateResponse(request, 'manager/list_user_profiles.html', context={'users': users})

@login_required
def edit_reminder(request):
    reminder_id = request.GET['id']
    reminder = Reminder.objects.get(id=reminder_id)
    if request.method == "GET":
        reminder_form = ReminderEditForm(instance=reminder)
    else:
        reminder_form = ReminderEditForm(request.POST, instance=reminder)
        user = reminder_form.save()
    context = {
        'id': reminder.id,
        'username': reminder.user.username,
        'form': reminder_form,
    }
    return TemplateResponse(request, 'manager/edit_reminder.html', context)

@login_required
def list_user_reminders(request):
    username = request.GET['username']
    user = get_user_model().objects.get(username=username)
    reminders = Reminder.objects.filter(user=user)
    return TemplateResponse(
        request,
        'manager/list_user_reminders.html',
        context={
            'username': username,
            'reminders': reminders
        }
    )

@login_required
def manage_user_profile(request):
    username = request.GET['username']
    if 'message' in request.GET:
        message = request.GET['message'].replace("+", " ")
    else:
        message = ""
    user = get_user_model().objects.get(username=username)
    if request.method == "GET":
        user_form = UserEditForm(instance=user)
    else:
        user_form = UserEditForm(request.POST, instance=user)
        user = user_form.save()
        message = "Utente modificato con successo"
    context = {
        'username': username,
        'email': user.email,
        'message': message,
        'user_form': user_form,
        'fields': get_user_profile_forms(user, request.POST)
    }
    #if request.method == "POST":
    #    x = "a" + 3
    return TemplateResponse(request, 'manager/manage_user_profile.html', context=context)



