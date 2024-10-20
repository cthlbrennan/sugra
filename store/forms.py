from django import forms
from allauth.account.forms import SignupForm
from .models import User

class CustomSignupForm(SignupForm):
    USER_TYPE_CHOICES = [
        ('gamer', 'Gamer'),
        ('developer', 'Developer'),
    ]
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.user_type = self.cleaned_data['user_type']
        user.save()
        return user
    
class UserTypeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['user_type']