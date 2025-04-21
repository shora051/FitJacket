from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)  # Allow null values
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Allow null values
    weight = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)  # Allow null values
    bio = models.TextField(null=True, blank=True)  # Already optional

    def __str__(self):
        return f"{self.user.username}'s Profile"
