from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError
from .models import User

class CustomSignupForm(SignupForm):
    USER_TYPE_CHOICES = [
        ('gamer', 'Gamer'),
        ('developer', 'Developer'),
    ]
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)
    username = forms.CharField(max_length=30, label='Username')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.user_type = self.cleaned_data['user_type']
        user.save()
        return user
    
class UserTypeAndPasswordForm(SetPasswordForm):
    USER_TYPE_CHOICES = [
        ('gamer', 'Gamer'),
        ('developer', 'Developer'),
    ]
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.RadioSelect)
    username = forms.CharField(max_length=150)

    class Meta:
        model = User
        fields = ['username', 'user_type', 'new_password1', 'new_password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
        return user