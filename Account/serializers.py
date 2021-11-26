from django.core import exceptions
from django.contrib.auth import password_validation
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError,transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from djoser import utils
from djoser.conf import settings
from rest_framework.exceptions import ValidationError

from .models import *

"""
Serializers:

- RegisterUserSerializer
- PasswordResetPhoneSerializer
- PasswordResetPhoneConfirmSerializer
- TokenToUserSerializer
- TokenForChangeUserDataSerializer
"""

class ActivationUserSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    default_error_messages = {
        "invalid_token": settings.CONSTANTS.messages.INVALID_TOKEN_ERROR,
        "invalid_uid": settings.CONSTANTS.messages.INVALID_UID_ERROR,
        "stale_token": settings.CONSTANTS.messages.STALE_TOKEN_ERROR,
    }

    def validate(self, attrs):
        try:
            uid = utils.decode_uid(attrs['uid'])
            user = User.objects.get(pk=uid)

        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            key_error = "invalid_uid"
            raise ValidationError(
                {"uid": [self.error_messages[key_error]]}, code=key_error
            )

        is_token_valid = default_token_generator.check_token(
            user, attrs['token']
        )

        if is_token_valid:
            if not user.is_active:
                return user.id
            raise exceptions.PermissionDenied(self.error_messages["stale_token"])
        else:
            key_error = "invalid_token"
            raise ValidationError(
                {"token": [self.error_messages[key_error]]}, code=key_error
            )

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    default_error_messages = { "cannot_create_user": settings.CONSTANTS.messages.CANNOT_CREATE_USER_ERROR }

    class Meta:
        model = User
        fields = ['email', 'phone', 'password', 'first_name', 'last_name' , 'middle_name']

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")

        try:
            password_validation.validate_password(password, user)
        
        except exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError({"password": serializer_error["non_field_errors"]})

        return attrs

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")

        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            if settings.SEND_ACTIVATION_EMAIL:
                user.is_active = False
                user.save(update_fields=["is_active"])

        return user

class RegisterUserSerializer(serializers.ModelSerializer):
    """
    Serializer for user register
    """

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'middle_name', 'phone']

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        if validated_data['first_name'] == '' and validated_data['last_name'] == '' \
        and validated_data['middle_name'] == '':
            user.first_name = user.id
            user.save()

        return user

    def validate_password(self, value):
        password_validation.validate_password(value, self)
        return value


class PasswordResetPhoneSerializer(serializers.Serializer):
    """
    Serializer for start password reset by phone
    """

    phone = serializers.CharField(max_length=15, label = 'Phone')


class PasswordResetPhoneConfirmSerializer(serializers.Serializer):
    """
    Serializer of confirm password reset by phone
    """

    code = serializers.CharField(max_length=6, label = 'Code')
    new_password = serializers.CharField(max_length=64, label = 'New password')
    re_new_password = serializers.CharField(max_length=64, label = 'Re new password')

    def validate_code(self, value):
        if len(value)!=6:
            raise serializers.ValidationError("Code must consist of 6 symbols!")
        else:
            return value

    def validate_new_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value

    def validate_re_new_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value

class TokenToUserSerializer(serializers.Serializer):
    """
    Serializer for converting token to user
    """

    token = serializers.CharField(max_length=40, label = 'Token')

    def validate_token(self, token):
        try:
            token = Token.objects.get(key = token)
        except:
            raise serializers.ValidationError("User with this token do not exists!")
        return token.user

class TokenForChangeUserDataSerializer(serializers.Serializer):
    """
    Serializer of changing user's data
    """
    
    token = serializers.CharField(max_length=40, label = 'Token')
    first_name = serializers.CharField(max_length=150, required = False, label = 'First name')
    last_name = serializers.CharField(max_length=150, required = False, label = 'Last name')
    middle_name = serializers.CharField(max_length=150, required = False, label = 'Middle name')
    password = serializers.CharField(max_length=64, required = False, label = 'New password')
    email = serializers.EmailField(required = False, label = 'Email')
    phone = serializers.CharField(max_length=15, required = False, label = 'Phone')

    def validate_token(self, token):
        try:
            token = Token.objects.get(key = token)
        except:
            raise serializers.ValidationError("User with this token do not exists!")
        return token.user

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value
