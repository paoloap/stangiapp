from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from .auth import generate_access_token, generate_refresh_token

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes

import jwt
from django.conf import settings
from django.core import serializers
from .serializers import UserSerializer
from .logic import *
import requests
from django.middleware.csrf import get_token
from .forms import UploadFileForm
from .seafile import upload_to_sf, delete_file

from django.core.management.utils import get_random_secret_key

@api_view(['GET'])
def user_profile(request):
    user = request.user
    result = get_user_profile(user)
    return Response({
        'user': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile': result
    })

@api_view(['GET'])
def user_reminders(request):
    user = request.user
    reminders_list = get_user_reminders_with_links(user)
    response = Response({'user': user.username, 'reminders': reminders_list })
    add_log(user, "ListReminders", "OK - user: {}".format(user.username))
    return response

@api_view(['GET'])
def global_attachments(request):
    user= request.user
    result = get_global_attachments(user)
    response = Response()
    if result["error"]:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        response.data = {
            "user": user.username,
            "error": "server_error"
        }
    else:
        response.status_code = status.HTTP_200_OK
        response.data = {
            "user": user.username,
            "file_list": result["file_list"]
        }
    return response

@api_view(['GET'])
def open_reminder(request):
    user = request.user
    reminder_id = request.query_params['reminder_id']
    reminder_data = get_reminder_data(user, reminder_id)
    result = reminder_data['result']
    if result == 'TAR':
        #x = "ciao" + 7
        response = Response()
        file_url = settings.PROTECTED_URL + 'down/' + reminder_data['file_name']
        response['X-Accel-Redirect'] = file_url
        #response['Access-Control-Allow-Origin'] = '*'
        #response['Access-Control-Allow-Headers'] = 'X-Requested-With'
        #response['Content-Type'] = 'application/x-tar'
    elif result == 'EMPTY':
        response = Response({
            'user': user.username,
            'msg': 'no files downloaded for reminder {}'.format(reminder_id)
        })
    else:
        response = Response({
            'user': user.username,
            'msg': 'error downloading files for reminder {}'.format(reminder_id),
            'detail': reminder_data['msg']
        })
    add_log(user, "OpenReminder", "OK - reminder: {}, user: {}".format(reminder_id, user.username))
    return response

@api_view(['GET'])
def download_attachment(request):
    user = request.user
    repo_type = request.query_params["repo_type"]
    reminder_id = request.query_params["reminder_id"]
    file_name = request.query_params["file_name"]
    attachment_fetch = get_attachment(user, reminder_id, repo_type, file_name)
    result = attachment_fetch["result"]
    if result == "ok":
        response = Response()
        response["Content-Disposition"] = "attachment; filename={0}".format(file_name)
        file_url = settings.PROTECTED_URL + "/down/" + file_name
        response["X-Accel-Redirect"] = file_url
    elif result == "ko":
        if attachment_fetch["error_type"] == "client":
            response = Response()
            response.status_code = status.HTTP_400_BAD_REQUEST
            response.data = {
                "user": user.username,
                "error": attachment_fetch["error_msg"]
            }
        else:
            response = Response()
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response.data = {
                "user": user.username,
                "error": "server_error"
            }
    #add_log(user, "GetDownload", "OK - reminder: {}, user: {}".format(reminder_id, user.username))
    #x = 5 + "a"
    return response

# @api_view(['GET'])
# def initialize_db(request):
#     secret = get_user_profile(request.secret)
#     if (secret == "asdasdasdasd"):
#         initdb()
#     return Response({'result': "ok" })
@api_view(['PUT'])
def change_reminder_status(request):
    user = request.user
    reminder_id = request.data.get("reminder_id")
    reminder_status_name = request.data.get("status")
    outcome = set_reminder_status(user, reminder_id, reminder_status_name, False)
    response = Response()
    result = outcome["result"]
    if result == "ok":
        response.status_code = status.HTTP_200_OK
        response.data = {
            'user': user.username,
            'old_status': outcome["old_status"],
            'new_status': outcome["new_status"]
        }
    else:
        if outcome["error_type"] == "client":
            response.status_code = status.HTTP_400_BAD_REQUEST
            response.data = {
                "user": user.username,
                "error": outcome["error_msg"]
            }
        else:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response.data = {
                "user": user.username,
                "error": "server_error"
            }
    return response

@api_view(['DELETE'])
def delete_attachment(request):
    user = request.user
    file_name = request.data.get("file_name")
    result = delete_file(user, file_name)
    response = Response()
    if result:
        response.status_code = status.HTTP_200_OK
        response.data = {
            'user': user.username,
            'result': "success"
        }
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        response.data = {
            'user': user.username,
            'result': "error"
        }
    return response


@api_view(['PUT'])
@csrf_protect
def change_password(request):
    user = request.user
    password = request.data.get('password')
    password2 = request.data.get('password2')
    old_password = request.data.get('old_password')
    log_msg = ""
    response = Response()
    if password != password2:
        #raise exceptions.ValueError('passwords don\'t match')
        response.data = {
            'user': user.username,
            'result': 'API_ERROR',
            'message': 'KO: passwords don\t match'
        }
        log_msg = "KO - passwords don't match"
    elif (not user.check_password(old_password)):
        #raise exceptions.AuthenticationFailed('wrong password')
        response.data = {
            'user': user.username,
            'result': 'API_ERROR',
            'message': 'KO: wrong password'
        }
        log_msg = "KO - wrong password"
    else:
        sf_session_result = init_cloud(user, password)
        if sf_session_result.startswith('OK'):
            user.set_password(password)
            user.save()
            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)
            response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
            response.data = {
                'user': user.username,
                'result': 'OK',
                'message': 'password changed',
                'access_token': access_token
            }
            log_msg = "OK"
        else:
            response.data = {
                'user': user.username,
                'result': 'SF_ERROR',
                'message': sf_session_result
            }
            log_msg = "KO - Seafile error - {}".format(sf_session_result)
    add_log(user, "PasswordChange", "{} - user: {}".format(log_msg, user.username))
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login_view(request):
    User = get_user_model()
    username = request.data.get('username')
    password = request.data.get('password')
    response = Response()
    if (username is None) or (password is None):
        raise exceptions.AuthenticationFailed(
            'username and password required')
    user = User.objects.filter(username=username).first()
    if(user is None):
        raise exceptions.AuthenticationFailed('user not found')
    if (not user.check_password(password)):
        add_log(user, "Login", "KO - wrong password (username: {})".format(username))
        raise exceptions.AuthenticationFailed('wrong password')
    #generate_test_data(user)
    sf_response = init_cloud(user, password)
    serialized_user = UserSerializer(user).data
    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)
    response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
    response.data = {
        'access_token': access_token,
        'user': serialized_user,
        'cloud_sync': sf_response
    }
    add_log(user, "Login", "OK - user: {}".format(username))

    return response

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def refresh_token_view(request):
    User = get_user_model()
    refresh_token = request.COOKIES.get('refreshtoken')
    if refresh_token is None:
        raise exceptions.AuthenticationFailed(
            'Authentication credentials were not provided.')
    try:
        payload = jwt.decode(
            refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed('expired refresh token, please login again.')
    user = User.objects.filter(id=payload.get('user_id')).first()
    if user is None:
        raise exceptions.AuthenticationFailed('User not found')
    if not user.is_active:
        raise exceptions.AuthenticationFailed('user is inactive')
    access_token = generate_access_token(user)
    return Response({'access_token': access_token})

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def logout(request):
    User = get_user_model()
    refresh_token = request.COOKIES.get('refreshtoken')
    if refresh_token is None:
        return Response({'result': 'no_token'})
    response = Response({'result': 'token_deleted'})
    response.delete_cookie("refreshtoken")
    return response

#@permission_classes([AllowAny])
#@csrf_protect
#def attach_file(request):
#    User = get_user_model()
#    reminder_id = request.GET['r']
#    refresh_token = request.COOKIES.get('refreshtoken')
#    frontend_url = f"{settings.FRONTEND_URL}reminders?reminder_id={reminder_id}&page=left"
#    if refresh_token is None:
#        raise exceptions.AuthenticationFailed(
#            'Authentication credentials were not provided.')
#    try:
#        payload = jwt.decode(
#            refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=['HS256'])
#    except jwt.ExpiredSignatureError:
#        raise exceptions.AuthenticationFailed('expired refresh token, please login again.')
#    user = User.objects.filter(id=payload.get('user_id')).first()
#    if user is None:
#        raise exceptions.AuthenticationFailed('User not found')
#    if not user.is_active:
#        raise exceptions.AuthenticationFailed('user is inactive')
#    if request.method == 'POST' and request.FILES['myfile']:
#        f = request.FILES.get('myfile')
#        file_name = f.name
#        file_type = f.content_type
#        rename_tmpl = '_{}_{}'
#        rename = rename_tmpl.format(reminder_id, f.name)
#        with open(settings.UPLOAD_PATH / rename, 'wb+') as destination:
#            for chunk in f.chunks():
#                destination.write(chunk)
#        result = upload_to_sf(user, rename)
#        if result == "OK":
#            return redirect(frontend_url, permanent=True)
#    return render(request, 'pages/attach_file.html', {"frontend_url": frontend_url, })

@api_view(['POST'])
@csrf_protect
def attach_file(request):
    user = request.user
    f = request.FILES.get('attachment')
    file_name = f.name
    file_type = f.content_type
    reminder_id = request.data.get('reminder_id')
    
    rename_tmpl = '_{}_{}'
    rename = rename_tmpl.format(reminder_id, f.name)
    with open(settings.UPLOAD_PATH / rename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    result = upload_to_sf(user, rename)
    add_log(user, "FileUpload", "{} - file: {}, user: {}".format(result, file_name, user.username))
    return Response({"result": result, "name": rename, "size": f.size})
    #form = UploadFileForm(request.POST, request.FILES)

    #if form.is_valid():
    #    result = attach_file(user, reminder_id, attachment)
    #    return Response(result)
    #else:
    #    return Response({'result': 'ERROR', 'msg': 'wrong form data'})



def password_reset_request(request):
    if request.method == "POST":
        if "activate_account" in request.POST:
            # request activation sent from manager
            data = request.POST["activate_account"]
            subject = "Attivazione account"
            email_template_name = "../templates/password/account_activation_email.txt"
            user = get_user_model().objects.get(email=data)
            redirect_link = "/manager/modifica_utente?username={}&message=Account+attivato!".format(user.username)
        else:
            password_reset_form = PasswordResetForm(request.POST)
            if password_reset_form.is_valid():
                data = password_reset_form.cleaned_data['email']
                subject = "Password Reset Requested"
                email_template_name = "../templates/password/password_reset_email.txt"
                user = get_user_model().objects.get(email=data)
                redirect_link = "/password_reset/done"
        if user:
            c = {
                "email":user.email,
                'domain':settings.ALLOWED_HOSTS[0],
                'site_name': 'Website',
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
            }
            email = render_to_string(email_template_name, c)
            try:
                send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            user.is_active = True
            user.save()
            return redirect(redirect_link)
    context = {
        "password_reset_form": PasswordResetForm()
    }
    return render(
        request=request,
        template_name="../templates/password/password_reset.html",
        context=context
    )
