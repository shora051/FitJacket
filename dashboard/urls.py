from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard.index'),
    path('learn/', views.learn, name='dashboard.learn'),
    path('api/exercises/', views.fetch_exercises, name='dashboard.api.exercises'),
    path('api/chatbot/', views.chatbot_query, name='dashboard.api.chatbot'),
]