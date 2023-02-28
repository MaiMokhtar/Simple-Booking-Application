from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.core.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, Studio, Reservation, StudioEmployee
from .serializers import UserSerializer, StudioSerializer, ReservationSerializer, StudioEmployeeSerializer, \
    StudioTokenObtainPairSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class StudioViewSet(ModelViewSet):
    queryset = Studio.objects.all()
    serializer_class = StudioSerializer
    permission_classes = [IsAuthenticated]


class ReservationViewSet(ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_customer:
            # Filter reservations by customer
            return Reservation.objects.filter(customer=user)

        elif user.is_employee:
            # Filter reservations by studio
            studio = user.studioemployee.studio
            return Reservation.objects.filter(studio=studio)

        elif user.is_owner:
            # Filter reservations by all studios owned by user
            owned_studios = Studio.objects.filter(owner=user)
            return Reservation.objects.filter(studio__in=owned_studios)

        else:
            # Raise permission denied if user has no role
            raise PermissionDenied("User has no role assigned.")

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.is_customer:
            if obj != user:
                raise PermissionDenied("You don't have permission to view this reservation.")

        elif user.is_employee:
            studio = user.studioemployee.studio
            if obj.studio != studio:
                raise PermissionDenied("You don't have permission to view this reservation.")

        elif user.is_owner:
            studios = Studio.objects.filter(owner=user)
            if obj.studio not in studios:
                raise PermissionDenied("You don't have permission to view this reservation.")
        return obj


class IsStudioOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.studio.owner == request.user

    def has_permission(self, request, view):
        user = request.user
        studio_id = request.query_params.get('studio_id')
        if user.is_authenticated and user.is_owner and studio_id:
            return user.studios.filter(id=studio_id).exists()
        else:
            return False


class StudioEmployeeViewSet(ModelViewSet):
    queryset = StudioEmployee.objects.all()
    serializer_class = StudioEmployeeSerializer
    permission_classes = [IsAuthenticated, IsStudioOwner]

    def get_queryset(self):
        user = self.request.user
        return StudioEmployee.objects.filter(studio__owner=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudioTokenObtainPairView(TokenObtainPairView):
    serializer_class = StudioTokenObtainPairSerializer
