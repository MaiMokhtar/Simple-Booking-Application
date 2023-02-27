from django.db import models
from users.models import User


class Studio(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='studios')
    employees = models.ManyToManyField(User, related_name='studios_employee')

    def __str__(self):
        return self.name


class Reservation(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('studio', 'date', 'time')


class StudioEmployee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
