from django.db import models
from django.db.models import Sum
from users.models import User
from django.core.exceptions import ValidationError


class Studio(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='studios')
    employees = models.ManyToManyField(User, related_name='studios_employee')
    max_customers_per_day = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def assign_employee(self, user):
        if not user.is_employee:
            raise ValueError("User is not an employee")
        if self.employees.filter(id=user.id).exists():
            raise ValueError("Employee is already assigned to this studio")
        # self.employees.add(user)
        StudioEmployee.objects.create(studio=self, user=user)


class Reservation(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('studio', 'date', 'time')

    def validate_max_customers_per_day(self):
        max_customers_per_day = self.studio.max_customers_per_day
        date = self.date
        num_customers = Reservation.objects.filter(studio=self.studio, date=date).aggregate(Sum('num_customers'))[
                            'num_customers__sum'] or 0
        if num_customers + self.num_customers > max_customers_per_day:
            raise ValidationError(
                f"The maximum number of customers for {date} at {self.studio} has already been reached.")

    def save(self, *args, **kwargs):
        self.validate_max_customers_per_day()
        super().save(*args, **kwargs)


class StudioEmployee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)

