from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='accounts.signup'),
    path('login/', views.login_view, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
    path('profile/setup/', views.profile_setup, name='accounts.profile_setup'),
    path('profile/settings/', views.profile_settings, name='accounts.profile_settings'),  # New URL
    path('profile/', views.profile_view, name='accounts.profile'),
    
    # Password Reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             success_url='/accounts/password-reset/done/'
         ),
         name='accounts.password_reset'),
    
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/login/'
         ),
         name='password_reset_confirm'),
]