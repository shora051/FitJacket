from django.db import models

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
