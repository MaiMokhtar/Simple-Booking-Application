from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.core.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Studio, Reservation, StudioEmployee
from .serializers import StudioSerializer, ReservationSerializer, StudioEmployeeSerializer, \
    StudioTokenObtainPairSerializer


class StudioViewSet(ModelViewSet):
    """A view set for CRUD operations on Studio objects.

    Attributes:
        queryset (QuerySet): The queryset of Studio objects to be used for the view set.
        serializer_class (Serializer): The serializer class to be used for the view set.
        permission_classes (List[Permission]): The list of permissions to be checked before allowing access
                                               to the view set.
    """
    queryset = Studio.objects.all()
    serializer_class = StudioSerializer
    permission_classes = [IsAuthenticated]


class ReservationViewSet(ModelViewSet):
    """API endpoint that allows reservations to be viewed or edited.

    Attributes:
        queryset (QuerySet): A queryset of all Reservation objects.
        serializer_class (Serializer): The serializer class to be used for Reservation objects.
        permission_classes (list): The list of permission classes that will be applied to all requests.

    Methods:
        get_queryset(): Returns a filtered queryset based on the requesting user's role.
        get_object(): Returns the Reservation object for the requested reservation ID, with additional permission checks based on the requesting user's role.
    """
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get the list of Reservations based on the user's role.

        Args:
            self (ReservationViewSet): Instance of ReservationViewSet

        Returns:
            Queryset: Filtered queryset based on the user's role.

        Raises:
            PermissionDenied: If user's role is not defined or user has no permission to access this view.
        """
        user = self.request.user

        if user.is_customer:
            # Filter reservations by customer
            return Reservation.objects.filter(customer=user)

        elif user.is_employee:
            # Filter reservations by studio
            studio = user.studioemployee.studio
            return Reservation.objects.filter(studio=studio)

        elif user.is_studio_owner:
            # Filter reservations by all studios owned by user
            owned_studios = Studio.objects.filter(owner=user)
            return Reservation.objects.filter(studio__in=owned_studios)

        else:
            # Raise permission denied if user has no role
            raise PermissionDenied("User has no role assigned.")

    def get_object(self):
        """Retrieve and return the requested reservation object based on the user's permissions.

        Raises a `PermissionDenied` exception if the user doesn't have the necessary permissions to view the reservation.

        Returns:
            A `Reservation` object.

        Raises:
            PermissionDenied: If the user doesn't have the necessary permissions to view the reservation.
        """
        obj = super().get_object()
        user = self.request.user
        if user.is_customer:
            if obj != user:
                raise PermissionDenied("You don't have permission to view this reservation.")

        elif user.is_employee:
            studio = user.studioemployee.studio
            if obj.studio != studio:
                raise PermissionDenied("You don't have permission to view this reservation.")

        elif user.is_studio_owner:
            studios = Studio.objects.filter(owner=user)
            if obj.studio not in studios:
                raise PermissionDenied("You don't have permission to view this reservation.")
        return obj


class IsStudioOwner(BasePermission):
    """Permission class that allows access only to studio owners.

    In order to access the view, the requesting user must be authenticated,
    have the 'is_studio_owner' flag set to True, and own the studio being accessed.
    """
    def has_object_permission(self, request, view, obj):
        """Check if the requesting user owns the studio of the requested object.

        Args:
            request: The HTTP request.
            view: The Django view.
            obj: The object being requested.

        Returns:
            True if the user owns the studio of the requested object, False otherwise.
        """
        return obj.studio.owner == request.user

    def has_permission(self, request, view):
        """Check if the requesting user owns the specified studio.

        Args:
            request: The HTTP request.
            view: The Django view.

        Returns:
            True if the user owns the specified studio, False otherwise.
        """
        user = request.user
        studio_id = request.query_params.get('studio_id')
        if user.is_authenticated and user.is_studio_owner and studio_id:
            return user.studios.filter(id=studio_id).exists()
        else:
            return False


class StudioEmployeeViewSet(ModelViewSet):
    """A viewset for managing studio employees.

    Attributes:
        queryset: A QuerySet of all StudioEmployee objects.
        serializer_class: The serializer class to use for this viewset.
        permission_classes: A list of permission classes that each user must satisfy to access this viewset.

    Methods:
        get_queryset(): Returns a QuerySet of StudioEmployee objects filtered by the owner of the studio.
        perform_create(serializer): Saves the new StudioEmployee instance with the current user as the owner.
    """
    queryset = StudioEmployee.objects.all()
    serializer_class = StudioEmployeeSerializer
    permission_classes = [IsAuthenticated, IsStudioOwner]

    def get_queryset(self):
        """Returns a QuerySet of StudioEmployee objects filtered by the owner of the studio.

        Returns:
            A QuerySet of StudioEmployee objects filtered by the owner of the studio.
        """
        user = self.request.user
        return StudioEmployee.objects.filter(studio__owner=user)

    def perform_create(self, serializer):
        """Saves the new StudioEmployee instance with the current user as the owner.

        Args:
            serializer: The serializer instance to use for creating the new StudioEmployee instance.

        Returns:
            None
        """
        serializer.save(user=self.request.user)


class StudioTokenObtainPairView(TokenObtainPairView):
    """View that returns an access and refresh token for a studio user.

    Extends the `TokenObtainPairView` class and uses the `StudioTokenObtainPairSerializer`
    to generate tokens with an associated studio ID.

    Attributes:
        serializer_class (StudioTokenObtainPairSerializer): The serializer class to use for token generation.
    """
    serializer_class = StudioTokenObtainPairSerializer
