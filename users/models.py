from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
import secrets

NULLABLE = {'null': True, 'blank': True}


class User(AbstractUser, PermissionsMixin):

    username = None
    phone_number = models.CharField(max_length=20, verbose_name='Номер телефона', unique=True)
    name = models.CharField(max_length=70, verbose_name='Имя', **NULLABLE)
    own_code = models.CharField(max_length=6, verbose_name='Инвайт код')
    invite_code = models.ForeignKey('self', on_delete=models.RESTRICT, **NULLABLE)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.name}: {self.phone_number}'

    def create_own_code(self):
        while own_code := secrets.token_hex(3):
            if User.objects.filter(own_code=own_code).exists():
                continue
            self.own_code = own_code
            self.save()
            break

    @classmethod
    def create_user(cls, credentials: dict):
        user = cls(**credentials)
        user.create_own_code()
        user.save()
        return user
