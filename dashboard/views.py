from django.shortcuts import render

# Create your views here.

def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')

def create_plan_view(request):
    return render(request, 'dashboard/createPlan.html')
