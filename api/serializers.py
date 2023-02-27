from rest_framework.serializers import ModelSerializer, ValidationError
from .models import User, Studio, Reservation, StudioEmployee


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


class StudioEmployeeSerializer(ModelSerializer):
    class Meta:
        model = StudioEmployee
        fields = ('id', 'studio', 'employee')

    def validate(self, data):
        # Check that the studio belongs to the requesting user
        user = self.context['request'].user
        studio = data['studio']
        if studio.owner != user:
            raise ValidationError("You don't have permission to assign employees to this studio.")

        # Check that the employee isn't already assigned to another studio
        employee = data['employee']
        if StudioEmployee.objects.filter(employee=employee).exists():
            raise ValidationError("This employee is already assigned to another studio.")

        return data

    def create(self, validated_data):
        # Create and return the new StudioEmployee object
        return StudioEmployee.objects.create(**validated_data)
