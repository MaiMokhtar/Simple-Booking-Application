from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'is_studio_owner', 'is_employee', 'is_customer']

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        is_studio_owner = validated_data['is_studio_owner']
        is_employee = validated_data['is_employee']
        is_customer = validated_data['is_customer']

        if password != validated_data.pop('confirm_password'):
            raise serializers.ValidationError('Passwords do not match')

        user = User.objects.create_user(username=username, password=password, is_studio_owner=is_studio_owner,
                                        is_employee=is_employee, is_customer=is_customer)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    refresh = RefreshToken.for_user(user)
                    return {
                        'username': username,
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                else:
                    raise serializers.ValidationError("User is not active.")
            else:
                raise serializers.ValidationError("Incorrect username/password.")
        else:
            raise serializers.ValidationError("Both fields are required.")


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'is_studio_owner', 'is_employee', 'is_customer')
        read_only_fields = ('id',)


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        return data
