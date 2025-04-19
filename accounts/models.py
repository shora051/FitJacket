from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()  # Required field
    height = models.DecimalField(max_digits=5, decimal_places=2)  # Required field
    weight = models.DecimalField(max_digits=5, decimal_places=1)  # Required field
    bio = models.TextField(null=True, blank=True)  # Fitness Goal remains optional

    def __str__(self):
        return f"{self.user.username}'s Profile"
