from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard.index'),
    path('learn/', views.learn, name='dashboard.learn'),

    # Workout endpoints
    path('api/exercises/', views.fetch_exercises, name='dashboard.api.exercises'),
    path('api/chatbot/', views.chatbot_query, name='dashboard.api.chatbot'),
    path('api/plan-exercises/', views.search_exercises_for_plan, name='dashboard.api.plan_exercises'),
    path('api/workouts/', views.workout_api, name='dashboard.api.workouts'),
    path('api/workouts/create/', views.save_workout, name='save_workout'),
    path('api/workouts/<int:workout_id>/update/', views.update_workout, name='update_workout'),
    path('api/workouts/<int:workout_id>/delete/', views.delete_workout, name='delete_workout'),
    path('api/workouts/<int:workout_id>/', views.get_workout_details, name='get_workout_details'),
    path('api/workouts/<int:workout_id>/add-exercise/', views.add_exercise_to_workout, name='add_exercise_to_workout'),

    # Calendar & logging
    path('calendar/', views.calendar_view, name='dashboard.calendar'),
    path('log-workout/', views.log_workout, name='log_workout'),
    path('log-health/', views.log_health_ajax, name='log_health_ajax'),
    path('api/delete-workout-log/', views.delete_workout_log, name='delete_workout_log'),
    path('health-history/', views.health_history_view, name='dashboard.health_history'),
    path('health-history/edit/<int:log_id>/', views.edit_health_log, name='dashboard.edit_health_log'),
]

