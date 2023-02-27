from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, BasePermission

from .models import User, Studio, Reservation, StudioEmployee
from .serializers import UserSerializer, StudioSerializer, ReservationSerializer, StudioEmployeeSerializer


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


class IsStudioOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.studio.owner == request.user


class StudioEmployeeViewSet(ModelViewSet):
    queryset = StudioEmployee.objects.all()
    serializer_class = StudioEmployeeSerializer
    permission_classes = [IsAuthenticated, IsStudioOwner]

    def get_queryset(self):
        user = self.request.user
        return StudioEmployee.objects.filter(studio__owner=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
