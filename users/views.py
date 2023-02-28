from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView


from .models import User
from .serializers import UserTokenObtainPairSerializer, UserSerializer, SignupSerializer, LoginSerializer


class SignUpView(CreateAPIView):
    """View for creating a new user account.

    POST requests to this view with valid user data will create a new user account.

    Attributes:
        queryset (QuerySet): A QuerySet containing all User objects.
        serializer_class (SignupSerializer): The serializer class used to serialize/deserialize user data.
        permission_classes (list): A list of permission classes that determine who can access this view.

    Methods:
        post(request, *args, **kwargs): Handle POST requests to create a new user account.
    """
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):
    """View to obtain access and refresh JSON Web Tokens for authentication.

    Inherits from `TokenObtainPairView` and uses the `LoginSerializer` to validate user credentials and
    return the JWT tokens upon successful authentication.

    Attributes:
        serializer_class: The serializer class used for validating user credentials and obtaining tokens.
    """
    serializer_class = LoginSerializer


class UserViewSet(ModelViewSet):
    """A view set that handles CRUD operations for User objects.

    Attributes:
        queryset (QuerySet): The set of User objects to be displayed and manipulated.
        serializer_class (UserSerializer): The serializer class to be used for serializing and deserializing User objects.
        permission_classes (list): A list of permission classes that determine the permissions for the UserViewSet.

    Methods:
        list(request): Returns a serialized representation of all User objects in the queryset.
        retrieve(request, pk): Returns a serialized representation of a single User object with the specified primary key.
        create(request): Creates a new User object with the provided data and returns a serialized representation of
                         the new User object.
        update(request, pk): Updates the User object with the specified primary key with the provided data and returns
                             a serialized representation of the updated User object.
        partial_update(request, pk): Partially updates the User object with the specified primary key with the provided
                                     data and returns a serialized representation of the updated User object.
        destroy(request, pk): Deletes the User object with the specified primary key.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserTokenObtainPairView(TokenObtainPairView):
    """View that returns JWT tokens for a given user.

    Inherits from TokenObtainPairView and uses a custom serializer,
    UserTokenObtainPairSerializer, to validate the user's credentials.

    The tokens are returned as a JSON response containing the user's
    username, access token, and refresh token.

    HTTP Methods:
        - POST: Generates and returns JWT tokens for a user with valid credentials.

    Attributes:
        serializer_class: The serializer class to be used for validating the user's credentials.

    Returns:
        A JSON response containing the user's username, access token, and refresh token.

    Raises:
        HTTP 400 Bad Request: If the user's credentials are invalid.
        HTTP 401 Unauthorized: If the user is not authenticated.
    """
    serializer_class = UserTokenObtainPairSerializer
