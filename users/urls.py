from django.urls import path
from users.apps import UsersConfig
from users.views import *

app_name = UsersConfig.name

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfile.as_view(), name='profile'),
    path('invite/', UserSetInviteCodeView.as_view(), name='set_invite_code'),
]
