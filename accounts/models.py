from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    height = models.DecimalField(max_digits=5, decimal_places=2, help_text="Height in inches")
    weight = models.DecimalField(max_digits=5, decimal_places=1, help_text="Weight in pounds")
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
