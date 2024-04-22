from rest_framework import serializers
from users.models import User


class UserLoginSerializer(serializers.Serializer):

    name = serializers.CharField(min_length=3, max_length=70, required=False)
    phone_number = serializers.RegexField(r'^[\+]?[0-9]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$',
                                          min_length=12, max_length=20)


class SMSVerificationSerializer(serializers.Serializer):
    sms_code = serializers.CharField(max_length=4, min_length=4)


class UserPhoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('phone_number',)


class UserProfileSerializer(serializers.ModelSerializer):
    subscribers = UserPhoneSerializer(source='user_set.all', many=True, read_only=True)
    invite_code = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('pk', 'phone_number', 'own_code', 'invite_code', 'subscribers',)

    def get_invite_code(self, instance):
        if instance.invite_code:
            return instance.invite_code.own_code
        else:
            return None


class UserSetInviteCode(serializers.Serializer):
    invite_code = serializers.CharField(max_length=6, min_length=6)
