import re
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
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    username = forms.CharField(
        max_length=30,
        min_length=8,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
            'title': 'Username must be at least 8 characters long and include letters, numbers, and special characters',
            'oninvalid': 'this.setCustomValidity("Please check username requirements")',
            'oninput': 'this.setCustomValidity("")'
        })
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        
        if len(username) < 8:
            raise ValidationError(
                "Username must be at least 8 characters long."
            )
            
        pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'  # Use raw string        
        if not re.match(pattern, username):
            raise ValidationError(
                "Username must contain at least one letter, one number, and one special character (@$!%*#?&)."
            )
            
        if User.objects.filter(username=username).exists():
            raise ValidationError(
                "This username is already taken."
            )
            
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
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    username = forms.CharField(
        max_length=30,
        min_length=8,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
            'title': 'Username must be at least 8 characters long and include letters, numbers, and special characters',
            'oninvalid': 'this.setCustomValidity("Please check username requirements")',
            'oninput': 'this.setCustomValidity("")'
        })
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Tell us about yourself...'
        })
    )
    profile_picture = CloudinaryFileField(
        options={
            'crop': 'thumb',
            'width': 200,
            'height': 200,
            'folder': 'profile_pictures'
        },
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'user_type', 'bio', 'profile_picture', 'new_password1', 'new_password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 8:
            raise ValidationError(
                "Username must be at least 8 characters long."
            )
            
        pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'  # Use raw string        
        if not re.match(pattern, username):
            raise ValidationError(
                "Username must contain at least one letter, one number, and one special character (@$!%*#?&)."
            )
            
        # Check for uniqueness
        if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise ValidationError(
                "This username is already taken."
            )
            
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.user_type = self.cleaned_data['user_type']
        user.bio = self.cleaned_data.get('bio', '')
        
        # Handle profile picture upload
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Ensure we're getting the actual file from Cloudinary
            if hasattr(profile_picture, 'url'):
                user.profile_picture = profile_picture
            # If it's a direct file upload
            else:
                user.profile_picture = profile_picture
        
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
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'genre': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
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
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
        }

class UserProfilePictureForm(forms.ModelForm):
    profile_picture = CloudinaryFileField(
        options={
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
