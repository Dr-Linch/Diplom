from django.shortcuts import redirect
from users.serializers import *
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from users.services import make_otp
from rest_framework.exceptions import AuthenticationFailed
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from datetime import datetime, timedelta
from users.models import User
from django.conf import settings
from rest_framework.generics import GenericAPIView
from users.auth import MyAuthentication
from rest_framework.mixins import RetrieveModelMixin
import jwt
import time


class UserLoginView(APIView):

    def post(self, request: Request):
        if request.query_params.get('auth'):
            return self.verification(request)
        return self.get_sms_code(request)

    def get_sms_code(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():

            if str(serializer.data.get('phone_number'))[:2] != '79':
                raise AuthenticationFailed('Номер телефона должен начинаться на 79')

            auth_code, auth_token = self.create_sms_code(serializer.data)

            request.session['Token'] = jwt.decode(auth_token, settings.SECRET_KEY, algorithms=['HS256',])

            return Response(status=HTTP_200_OK, data={
                'Код для авторизации': auth_code,
                'Адрес авторизации': 'login/auth=1',
                'Поле для кода': 'sms_code',
            })
        return Response(status=HTTP_200_OK, data={
            'error': 'Ошибка авторизации'
        })

    def verification(self, request):
        serializer = SMSVerificationSerializer(data=request.data)

        if serializer.is_valid():
            user_sms_code = serializer.data.get('sms_code')
            sms_token = request.session.get('Token')

            if dict(sms_token).get('sms_code') != user_sms_code:
                raise AuthenticationFailed('Вы ввели неправильный код!')

            return self.authentication(request, dict(sms_token).get('credentials'))

    def authentication(self, request, data):
        data = dict(data)

        try:
            user = User.objects.get(**data)
        except ObjectDoesNotExist:
            user = User.create_user(data)

        user_token = self.create_ott(user)
        return Response(status=HTTP_200_OK, data={
            'Сообщение': 'Вы успешно авторизовались',
            'Ваш токен': user_token
        })

    @staticmethod
    def create_ott(user):
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(hours=2),
            'user_id': user.id,
        }
        return jwt.encode(payload, settings.SECRET_KEY)

    @staticmethod
    def create_sms_code(data):
        time.sleep(3)
        sms_code = make_otp()
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(seconds=60*5),
            'credentials': dict(data),
            'sms_code': sms_code,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        return sms_code, token


class UserProfile(GenericAPIView, RetrieveModelMixin):
    authentication_classes = (MyAuthentication,)
    permission_classes = [IsAuthenticated,]
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()

    def get(self, request):

        self.kwargs['pk'] = request.user.id
        return self.retrieve(request)


class UserSetInviteCodeView(APIView):
    authentication_classes = (MyAuthentication,)
    permission_classes = [IsAuthenticated, ]

    def post(self, request):

        serializer = UserSetInviteCode(data=request.data)

        if serializer.is_valid():
            if request.user.invite_code is not None:
                return Response(status=HTTP_400_BAD_REQUEST, data={'info': 'Вы уже вводили инвайт код'})
            if request.user.own_code == serializer.data.get('invite_code'):
                return Response(status=HTTP_400_BAD_REQUEST, data={'info': 'Вы не можете ввести свой инвайт код'})

            code_owner = User.objects.get(own_code=serializer.data.get('invite_code'))
            if code_owner:
                request.user.invite_code = code_owner
                request.user.save()
                return redirect('/profile')
            else:
                return Response(status=HTTP_400_BAD_REQUEST, data={'info': 'Такова кода не существует'})
