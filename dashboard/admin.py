from django.contrib import admin
from .models import Workout, Exercise

class ExerciseInline(admin.TabularInline):
    model = Exercise
    extra = 1

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'updated_at')
    list_filter = ('user', 'created_at')
    search_fields = ('name', 'user__username')
    inlines = [ExerciseInline]


