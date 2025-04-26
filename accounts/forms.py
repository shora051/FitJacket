from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from .models import UserProfile

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([
            f'<div class="alert alert-danger" role="alert"> {e}</div>' for e in self]))

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'email', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']  # Include email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'age', 'height', 'weight', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your age'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your height in inches'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your weight in pounds'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your fitness goal', 'rows': 4}),
        }
        labels = {
            'height': 'Height',
            'weight': 'Weight',
            'bio': 'Fitness Goal',
        }
        help_texts = {
            'height': None,
            'weight': None,
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # Make all fields required except for 'bio'
        for field_name in ['first_name', 'last_name', 'age', 'height', 'weight']:
            self.fields[field_name].required = True
        self.fields['bio'].required = False  # Fitness Goal is optional