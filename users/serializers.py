from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User


class SignupSerializer(serializers.ModelSerializer):
    """Serializes user signup data and creates a new user account.

    Attributes:
        password (serializers.CharField): Required password field for creating a new user.
        confirm_password (serializers.CharField): Required field for confirming the password.

    Methods:
        create(validated_data): Method to create a new user account based on validated data.

    Raises:
        serializers.ValidationError: If password and confirm_password do not match.
    """
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'is_studio_owner', 'is_employee', 'is_customer']

    def create(self, validated_data):
        """Create and return a new user instance, given the validated data.

        Args:
            validated_data (dict): The validated data to use for creating the user.
                Expected keys are 'username', 'password', 'confirm_password',
                'is_studio_owner', 'is_employee', and 'is_customer'.

        Raises:
            serializers.ValidationError: If the passwords in the validated data do not match.

        Returns:
            User: A new user instance with the given data.
        """
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
    """A serializer for user login.

    Attributes:
        username: A required field for the username of the user attempting to login.
        password: A required field for the password of the user attempting to login.

    Methods:
    validate(self, data): Validates the provided username and password by attempting to authenticate the user.
        If authentication is successful, generates a new access and refresh token for the user.
        Returns a dictionary containing the username, access token, and refresh token if authentication is successful.
        Raises a validation error if authentication fails or if the username and/or password fields are empty.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate the data submitted in a login request.

        Args:
            self (LoginSerializer): The LoginSerializer instance.
            data (dict): The data submitted in the login request.

        Returns:
            dict: A dictionary containing the username, access token, and refresh token if the username and password are
                  correct and the user is active.

        Raises:
            serializers.ValidationError: If the username and/or password are incorrect, the user is not active, or both
                                         fields are required.
        """
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
    """Serializer for User model.

    Attributes::
        id (read-only): The unique identifier of the user.
        username: The username of the user.
        is_studio_owner: A boolean indicating whether the user is a studio owner.
        is_employee: A boolean indicating whether the user is an employee.
        is_customer: A boolean indicating whether the user is a customer.
    """
    class Meta:
        """
        A Meta class to define metadata for the UserSerializer.

        Attributes:
            model: The model class that the serializer is based on.
            fields: A tuple of field names to include in the serialized output.
            read_only_fields: A tuple of read-only fields that should not be included in the serialized input.
        """
        model = User
        fields = ('id', 'username', 'is_studio_owner', 'is_employee', 'is_customer')
        read_only_fields = ('id',)


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    """A serializer that inherits from TokenObtainPairSerializer and validates user credentials for token authentication.

    Attributes:
        TokenObtainPairSerializer (class): A serializer that provides the token authentication view and validates
                                           user credentials.

    Methods:
        validate (function): Validates the user credentials and returns the validated data.
    """
    def validate(self, attrs):
        """Validates the user credentials and returns the validated data.

        Args:
             attrs (dict): A dictionary containing the attributes to be validated.

        Returns:
            data (dict): A dictionary that contains the validated data.
        """
        data = super().validate(attrs)
        return data
