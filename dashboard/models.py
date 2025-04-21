from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class FitnessResponse(models.Model):
    """
    Model to store common fitness questions and predefined responses
    This serves as a fallback when the Gemini API is unavailable
    """
    question_keywords = models.TextField(help_text="Keywords that trigger this response")
    response = models.TextField(help_text="The predefined response to return")
    
    def __str__(self):
        return self.question_keywords[:50]

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class Exercise(models.Model):
    workout = models.ForeignKey(Workout, related_name='exercises', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    sets = models.IntegerField()
    reps = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.sets}x{self.reps})"
