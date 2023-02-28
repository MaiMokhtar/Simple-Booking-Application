"""Module for defining Django models related to studio and reservation."""

from django.db import models
from django.db.models import Sum
from users.models import User
from django.core.exceptions import ValidationError


class Studio(models.Model):
    """Studio Model.

    It defines a studio object with the following attributes:

    - name (str): The name of the studio.
    - owner (User): The owner of the studio.
    - employees (ManyToManyField): The employees associated with the studio.
    - max_customers_per_day (int): The maximum number of customers per day that can be reserved.

    """
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='studios')
    employees = models.ManyToManyField(User, related_name='studios_employee')
    max_customers_per_day = models.IntegerField(default=10)

    def __str__(self):
        return self.name

    def assign_employee(self, user):
        """Assigns an employee to the Studio object.

        Args:
        self (Studio): The Studio object to which the employee will be assigned.
        user (User): The employee User object to assign to the Studio.

        Raises:
        ValueError: If the user is not an employee or if the employee is already assigned to this studio.

        Returns:
        None
        """
        if not user.is_employee:
            raise ValueError("User is not an employee")
        if self.employees.filter(id=user.id).exists():
            raise ValueError("Employee is already assigned to this studio")
        # self.employees.add(user)
        StudioEmployee.objects.create(studio=self, user=user)


class Reservation(models.Model):
    """Reservation Model.

    It defines a reservation object with the following attributes:

    - customer (User): The customer who made the reservation.
    - studio (Studio): The studio where the reservation is made.
    - date (date): The date of the reservation.
    - time (time): The time of the reservation.
    - notes (str, optional): Any additional notes for the reservation.

    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('studio', 'date', 'time')

    def validate_max_customers_per_day(self):
        """Validates if the number of customers for a reservation exceeds the maximum number of customers allowed
        per day for the associated studio.

        Args:
        self (Reservation): The Reservation object to validate.

        Raises:
        ValidationError: If the number of customers for the reservation exceeds the maximum number of customers
                         allowed per day.

        Returns:
        None
        """
        max_customers_per_day = self.studio.max_customers_per_day
        date = self.date
        num_customers = Reservation.objects.filter(studio=self.studio, date=date).aggregate(Sum('num_customers'))[
                            'num_customers__sum'] or 0
        if num_customers + self.num_customers > max_customers_per_day:
            raise ValidationError(
                f"The maximum number of customers for {date} at {self.studio} has already been reached.")

    def save(self, *args, **kwargs):
        """Saves the Reservation object after validating if the maximum number of customers allowed per day for
        the associated studio is not exceeded.

        Args:
        self (Reservation): The Reservation object to save.
        *args: Optional arguments to pass to the parent save method.
        **kwargs: Optional keyword arguments to pass to the parent save method.

        Raises:
        ValidationError: If the number of customers for the reservation exceeds the maximum number of customers
                         allowed per day.

        Returns:
        None
        """
        self.validate_max_customers_per_day()
        super().save(*args, **kwargs)


class StudioEmployee(models.Model):
    """StudioEmployee Model.

    It defines a relationship between a studio and an employee with the following attributes:

    - user (User): The employee associated with the studio.
    - studio (Studio): The studio where the employee works.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)

