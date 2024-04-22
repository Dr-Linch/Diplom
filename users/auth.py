import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import User


class MyAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Authorization'

    def authenticate(self, request):
        user = None

        auth_header = authentication.get_authorization_header(request).split()
        prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            raise Exception('Нет auht_header')

        token = jwt.decode(auth_header[-1], settings.SECRET_KEY, algorithms=['HS256',])

        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):

        try:
            payload = token
        except Exception:
            msg = 'Ошибка аутентификации. Невозможно декодировать токен'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(pk=payload['user_id'])
        except User.DoesNotExist:
            msg = 'Пользователь соответствующий данному токену не найден.'
            raise exceptions.AuthenticationFailed(msg)

        return user, token
