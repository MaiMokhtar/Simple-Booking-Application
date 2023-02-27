from rest_framework.serializers import ModelSerializer

from .models import User, Studio, Reservation


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class StudioSerializer(ModelSerializer):
    class Meta:
        model = Studio
        fields = '__all__'


class ReservationSerializer(ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'
