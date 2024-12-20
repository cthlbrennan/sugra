import re
from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError
from cloudinary.forms import CloudinaryFileField
from .models import User, Game


class CustomSignupForm(SignupForm):
    """Custom registration form extending allauth's SignupForm.

    Implements enhanced validation and styling for user registration.

    Features:
        - Custom username validation with pattern matching
        - Email confirmation
        - User type selection (Gamer/Developer)
        - Bootstrap styling integration
    """

    USERNAME_PATTERN = (
        r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'  # noqa: E501
    )
    USER_TYPE_CHOICES = [
        ('gamer', 'Gamer'),
        ('developer', 'Developer'),
    ]

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    email2 = forms.EmailField(
        label="Email (again)",
        widget=forms.EmailInput(attrs={
            'class': 'form-control w-100',
            'placeholder': 'Confirm your email'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control w-100',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control w-100',
            'placeholder': 'Confirm password'
        })
    )
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
            'style': 'margin-right: 10px;'
        })
    )
    username = forms.CharField(
        max_length=30,
        min_length=8,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': USERNAME_PATTERN,
            'title': (
                'Username must be at least 8 characters long and include '
                'letters, numbers, and special characters'
            ),
            'oninvalid': (
                'this.setCustomValidity("Please check username requirements")'
            ),
            'oninput': 'this.setCustomValidity("")'
        })
    )

    def clean_username(self):
        """Validate username against pattern requirements and uniqueness.

        Raises:
            ValidationError: If username doesn't meet length, pattern,
                           or uniqueness requirements
        """
        username = self.cleaned_data['username']

        if len(username) < 8:
            raise ValidationError(
                "Username must be at least 8 characters long."
                )

        if not re.match(self.USERNAME_PATTERN, username):
            raise ValidationError(
                "Username must contain at least one letter, one number, "
                "and one special character (@$!%*#?&).")

        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")

        return username

    def save(self, request):
        """Save the user and set additional attributes.

        Args:
            request: The HTTP request object

        Returns:
            User: The created user instance
        """
        user = super().save(request)
        user.user_type = self.cleaned_data['user_type']
        request.session['show_profile_setup'] = True
        user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (
                forms.TextInput,
                forms.EmailInput,
                forms.PasswordInput
            )):
                field.widget.attrs['class'] = 'form-control w-100'


class UserTypeAndPasswordForm(SetPasswordForm):
    """Combined form for setting user type and password.

    Used for social authentication completion and password reset.

    Features:
        - User type selection
        - Username validation
        - Bio and profile picture upload
        - Password setting/reset
    """

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
            'pattern': (
                r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])'
                r'[A-Za-z\d@$!%*#?&]{8,}$'
            ),
            'title': (
                'Username must be at least 8 characters long and include '
                'letters, numbers, and special characters'
                ),
            'oninvalid': (
                'this.setCustomValidity("Please check username '
                'requirements")'),
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
        fields = [
            'username',
            'user_type',
            'bio',
            'profile_picture',
            'new_password1',
            'new_password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update(
            {'class': 'form-control'})

    def clean_username(self):
        """Validate username with pattern matching and uniqueness check.

        Excludes current user when checking uniqueness.
        """
        username = self.cleaned_data['username']
        if len(username) < 8:
            raise ValidationError(
                "Username must be at least 8 characters long."
                )

        pattern = (
            r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])'
            r'[A-Za-z\d@$!%*#?&]{8,}$'
        )
        if not re.match(pattern, username):
            raise ValidationError(
                "Username must contain at least one letter, one number, "
                "and one special character (@$!%*#?&).")

        if User.objects.filter(username=username).exclude(
            pk=self.user.pk
        ).exists():
            raise ValidationError("This username is already taken.")

        return username

    def save(self, commit=True):
        """Save user with additional profile information.

        Args:
            commit: Whether to save to database immediately

        Returns:
            User: The updated user instance
        """
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.user_type = self.cleaned_data['user_type']
        user.bio = self.cleaned_data.get('bio', '')

        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            if hasattr(profile_picture, 'url'):
                user.profile_picture = profile_picture
            else:
                user.profile_picture = profile_picture

        if commit:
            user.save()
        return user


class GameForm(forms.ModelForm):
    """Form for game creation and editing.

    Features:
        - Basic game information fields
        - Multiple screenshot uploads
        - Price validation
        - Bootstrap styling
    """

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
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4}
            ),
            'genre': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_price(self):
        """Validate game price to ensure it meets minimum requirements.

        Minimum price: €0.50
        """
        price = self.cleaned_data.get('price')
        if price is None:
            raise forms.ValidationError("Price is required.")
        if price < 0.50:
            raise forms.ValidationError("Price must be at least €0.50.")
        return price


class UserBioForm(forms.ModelForm):
    """Form for updating user biography.

    Provides styled textarea for bio input.
    """

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
    """Form for updating user profile picture.

    Features:
        - Cloudinary integration
        - Automatic image cropping
        - Size standardization (200x200)
    """

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
