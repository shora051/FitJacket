from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='accounts.signup'),
    path('login/', views.login_view, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
    path('profile/setup/', views.profile_setup, name='accounts.profile_setup'),
    path('profile/settings/', views.profile_settings, name='accounts.profile_settings'),  # New URL
    path('profile/', views.profile_view, name='accounts.profile'),
]