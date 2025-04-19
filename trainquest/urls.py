from django.contrib import admin
from django.urls import path, include
from dashboard import views as dashboard_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),  # home page routing
    path('dashboard/', include('dashboard.urls')),  # dashboard routing
    path('accounts/', include('accounts.urls')),  # accounts routing
    path('dashboard/', dashboard_views.dashboard_view, name='dashboard'),  # Added dashboard route
    path('dashboard/createPlan', dashboard_views.create_plan_view, name='create_plan'),  # Added createPlan route
]

