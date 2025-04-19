from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import CustomUserCreationForm, CustomErrorList, UserProfileForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

def login_view(request):
    error_message = None
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home.index')
        else:
            error_message = "Invalid username or password. Please try again."
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {
        'template_data': {
            'form': form,
            'error_message': error_message
        }
    })

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'

    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})

@login_required
def profile_setup(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        return redirect('home.index')  # Redirect if profile exists
    except UserProfile.DoesNotExist:
        pass

    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('home.index')
    else:
        form = UserProfileForm()

    return render(request, 'accounts/profile_setup.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Use CustomUserCreationForm
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('accounts.profile_setup')
    else:
        form = CustomUserCreationForm()  # Use CustomUserCreationForm
    return render(request, 'accounts/signup.html', {'template_data': {'form': form}})

@login_required
def profile_settings(request):
    try:
        user_profile = request.user.userprofile
        if request.method == 'POST':
            form = UserProfileForm(request.POST, instance=user_profile)
            if form.is_valid():
                form.save()
                return redirect('accounts.profile_settings')
        else:
            form = UserProfileForm(instance=user_profile)
        return render(request, 'accounts/profile_settings.html', {'profile': user_profile, 'form': form})
    except UserProfile.DoesNotExist:
        return redirect('accounts.profile_setup')

@login_required
def profile_view(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        return redirect('accounts.profile_settings')  # Redirect to settings if profile exists
    except UserProfile.DoesNotExist:
        return redirect('accounts.profile_setup')  # Redirect to setup if no profile exists

