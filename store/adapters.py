from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email
from allauth.account.models import EmailAddress

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for handling social account authentication.
    Extends Django-allauth's DefaultSocialAccountAdapter to provide additional
    functionality for cart preservation and user type handling.
    """

    def pre_social_login(self, request, sociallogin):
        """
        Handles pre-login operations for social authentication.
        
        Args:
            request: The HTTP request object
            sociallogin: The social login object containing user information
        
        This method:
        1. Preserves the user's shopping cart during social login
        2. Connects existing users if they login with a known email
        3. Sets a temporary username for new users
        """
        # Store cart before social login to prevent loss during authentication
        old_cart = request.session.get('cart', {})
        
        # Try to get the user's email from the social login data
        email = user_email(sociallogin.user)
        if email:
            try:
                # Look for existing user with this email
                user = EmailAddress.objects.get(email=email).user
                # Connect the social account to the existing user
                sociallogin.connect(request, user)
                # Restore the user's cart after connection
                if old_cart:
                    request.session['cart'] = old_cart
            except EmailAddress.DoesNotExist:
                # If no user exists with this email, continue with new user creation
                pass

        # For new users, set a temporary username using their social account ID
        if not sociallogin.user.pk:  # Check pk instead of id
            sociallogin.user.username = f"user_{sociallogin.account.uid}"
            sociallogin.user.user_type = None

    def save_user(self, request, sociallogin, form=None):
        """
        Saves the user after social login and handles user type setup.
        
        Args:
            request: The HTTP request object
            sociallogin: The social login object containing user information
            form: Optional form data (default: None)
            
        Returns:
            User: The saved user object
        """
        user = super().save_user(request, sociallogin, form)
        # Flag new users who need to set their user type
        if not user.user_type:
            request.session['redirect_to_set_user_type'] = True
        return user