from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard.index'),
    path('learn/', views.learn, name='dashboard.learn'),
    path('api/exercises/', views.fetch_exercises, name='dashboard.api.exercises'),
    path('api/chatbot/', views.chatbot_query, name='dashboard.api.chatbot'),
    path('api/plan-exercises/', views.search_exercises_for_plan, name='dashboard.api.plan_exercises'),
    path('api/workouts/', views.workout_api, name='dashboard.api.workouts'),
    path('api/workouts/create/', views.save_workout, name='save_workout'),
    path('api/workouts/<int:workout_id>/update/', views.update_workout, name='update_workout'),
    path('api/workouts/<int:workout_id>/delete/', views.delete_workout, name='delete_workout'),
    path('api/workouts/<int:workout_id>/', views.get_workout_details, name='get_workout_details'),
    path('api/workouts/<int:workout_id>/add-exercise/', views.add_exercise_to_workout, name='add_exercise_to_workout'),
    path('calendar/', views.calendar_view, name='dashboard.calendar'),
    
    # Favorite exercise endpoints
    path('api/favorites/', views.favorite_exercise, name='favorite_exercise'),
    path('api/favorites/list/', views.get_favorite_exercises, name='get_favorite_exercises'),
    path('api/favorites/check/<str:exercise_name>/', views.is_favorite_exercise, name='is_favorite_exercise'),
    path('log-workout/', views.log_workout_ajax, name='log_workout_ajax'),
    path('log-health/', views.log_health_ajax, name='log_health_ajax'),


]