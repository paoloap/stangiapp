import jwt
from rest_framework.authentication import BaseAuthentication
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import exceptions
from django.conf import settings
from django.contrib.auth import get_user_model
#import logging


#logger = logging.getLogger(__file__)
class CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        #csrf_token = request.META.get('CSRF_COOKIE')
        #request_csrf_token = request.POST.get('csrfmiddlewaretoken', '')
        #raise exceptions.AuthenticationFailed(csrf_token + " - " + request_csrf_token)
        return reason
    #def process_view(self, request, callback, callback_args, callback_kwargs):

    #    csrf_token = request.META.get('CSRF_COOKIE')
    #    request_csrf_token = request.POST.get('csrfmiddlewaretoken', '')
    #    request_csrf_token = request.META.get(settings.CSRF_HEADER_NAME, '')
    #    #raise exceptions.AuthenticationFailed(csrf_token + " - " + request_csrf_token + " - " + settings.CSRF_HEADER_NAME)
    #    return super(CsrfViewMiddleware, self).process_view(...)




class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):

        User = get_user_model()
        authorization_header = request.headers.get('Authorization')

        if not authorization_header:
            return None
        try:
            access_token = authorization_header.split(' ')[1]
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('access_token expired')
        except IndexError:
            raise exceptions.AuthenticationFailed('Token prefix missing')

        user = User.objects.filter(id=payload['user_id']).first()
        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('user is inactive')

        self.enforce_csrf(request)
        return (user, None)

    def enforce_csrf(self, request):
        check = CSRFCheck()
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        print(reason)
        if reason:
            raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)
