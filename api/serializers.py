from rest_framework.serializers import ModelSerializer, ValidationError, IntegerField
from .models import Studio, Reservation, StudioEmployee
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


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


class StudioTokenObtainPairSerializer(TokenObtainPairSerializer):
    studio_id = IntegerField(required=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        data['studio_id'] = self.validated_data['studio_id']
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['studio_id'] = user.studio_employee.studio_id
        return token
