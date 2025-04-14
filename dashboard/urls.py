from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard.index'),
    path('exercises/', views.exercises, name='dashboard.exercises'),
    path('api/exercises/', views.fetch_exercises, name='dashboard.api.exercises'),
    path('api/chatbot/', views.chatbot_query, name='dashboard.api.chatbot'),
]