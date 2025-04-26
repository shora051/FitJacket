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


class DailyHealthLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    calories = models.PositiveIntegerField(null=True, blank=True)
    cardio_minutes = models.PositiveIntegerField(null=True, blank=True)
    steps = models.PositiveIntegerField(null=True, blank=True)
    water_intake_liters = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"Health Log for {self.user.username} on {self.date}"




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

class FavoriteExercise(models.Model):
    """Model to store user's favorite exercises"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_exercises')
    name = models.CharField(max_length=200)
    body_part = models.CharField(max_length=100, blank=True, null=True)
    equipment = models.CharField(max_length=100, blank=True, null=True)
    target = models.CharField(max_length=100, blank=True, null=True)
    gif_url = models.URLField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'name']  # Prevent duplicate favorites
        ordering = ['-added_at']  # Most recently added first
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"


class WorkoutLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout = models.ForeignKey(
        Workout,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    date = models.DateField()

    def __str__(self):
        name = self.workout.name if self.workout else "Rest"
        return f"{name!r} on {self.date} by {self.user.username}"


class HealthLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    calories = models.PositiveIntegerField(null=True, blank=True)
    cardio_minutes = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)  # New field

    def __str__(self):
        return f"Health stats for {self.user.username} on {self.date}"
