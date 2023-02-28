from rest_framework.serializers import ModelSerializer, ValidationError, IntegerField
from .models import Studio, Reservation, StudioEmployee
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class StudioSerializer(ModelSerializer):
    """A serializer class to convert the Studio model object into JSON format and vice versa.

    Attributes:
        model (Studio): The Studio model object that will be serialized.
        fields (tuple): A tuple of fields to include in the serialized output. In this case, all fields are included.

    Returns:
        Serialized Studio object in JSON format.
    """
    class Meta:
        model = Studio
        fields = '__all__'


class ReservationSerializer(ModelSerializer):
    """A serializer class to convert the Reservation model object into JSON format and vice versa.

    Attributes:
        model (Reservation): The Reservation model object that will be serialized.
        fields (tuple): A tuple of fields to include in the serialized output. In this case, all fields are included.

    Returns:
        Serialized Reservation object in JSON format.
    """
    class Meta:
        model = Reservation
        fields = '__all__'


class StudioEmployeeSerializer(ModelSerializer):
    """Serializes and deserializes StudioEmployee instances into JSON.

    Fields:
        id: The unique identifier of the StudioEmployee.
        studio: The studio that the employee is assigned to.
        employee: The user account of the employee.

    Methods:
        validate(self, data): Validates the data before creating a new StudioEmployee object.
        create(self, validated_data): Creates a new StudioEmployee object.

    Attributes:
        Meta: A class that contains metadata for the serializer, including the model to use and the fields to include.

    Raises:
        ValidationError: If the studio doesn't belong to the requesting user or the employee is already assigned to
                       another studio.
    """
    class Meta:
        """Metadata for the StudioEmployeeSerializer class.

        Attributes:
            model: The Django model to use for the serializer.
            fields: The fields to include in the serialized representation of the model. In this case, all fields.
        """
        model = StudioEmployee
        fields = ('id', 'studio', 'employee')

    def validate(self, data):
        """Validates the data before creating a new StudioEmployee object.

        Args:
            data: A dictionary containing the deserialized data from the request.

        Returns:
            The validated data dictionary.

        Raises:
            ValidationError: If the studio doesn't belong to the requesting user or the employee is already assigned
                             to another studio.
        """
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
        """Creates a new StudioEmployee object.

        Args:
            validated_data: A dictionary containing the validated data.

        Returns:
            The newly created StudioEmployee object.
        """
        # Create and return the new StudioEmployee object
        return StudioEmployee.objects.create(**validated_data)


class StudioTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer for obtaining a JSON Web Token (JWT) for a studio.

        Attributes:
            studio_id (IntegerField): The ID of the studio for which to obtain a token.

        Methods:
            validate(attrs): Validates the input data and returns the validated data.
            get_token(user): Generates and returns a token for the specified user.
        """
    studio_id = IntegerField(required=True)

    def validate(self, attrs):
        """Validate the studio_id in the request and return the validated data.

         Args:
            attrs: A dictionary containing the request attributes.

        Returns:
            A dictionary containing the validated data.
        """
        data = super().validate(attrs)
        data['studio_id'] = self.validated_data['studio_id']
        return data

    @classmethod
    def get_token(cls, user):
        """Return a JSON Web Token with the studio_id of the user.

        Args:
            user: The user object for which the token is generated.

        Returns:
            token: A JSON Web Token with the studio_id of the user.
        """
        token = super().get_token(user)
        token['studio_id'] = user.studio_employee.studio_id
        return token
