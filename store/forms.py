from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError
from cloudinary.forms import CloudinaryFileField
from .models import User, Game

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

class GameForm(forms.ModelForm):
    screenshot1 = CloudinaryFileField(
        options={'folder': 'game_screenshots'},
        required=False,
        help_text="Upload screenshot 1 (JPG or PNG only)"
    )
    screenshot2 = CloudinaryFileField(
        options={'folder': 'game_screenshots'},
        required=False,
        help_text="Upload screenshot 2 (JPG or PNG only)"
    )
    screenshot3 = CloudinaryFileField(
        options={'folder': 'game_screenshots'},
        required=False,
        help_text="Upload screenshot 3 (JPG or PNG only)"
    )

    class Meta:
        model = Game
        fields = ['title', 'description', 'genre', 'price', 'thumbnail']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Price must be 0 or greater.")
        return price

class UserBioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

class UserProfilePictureForm(forms.ModelForm):
    profile_picture = CloudinaryFileField(
        options = {
            'crop': 'thumb',
            'width': 200,
            'height': 200,
            'folder': 'profile_pictures'
        },
        required=False
    )

    class Meta:
        model = User
        fields = ['profile_picture']