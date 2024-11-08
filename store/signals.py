from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added
from django.contrib.auth import user_logged_in
from django.shortcuts import redirect
from allauth.account.signals import user_signed_up
from django.contrib import messages
from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.signals import user_logged_in
from .models import User, Game, Review, ReviewVote
from decimal import Decimal
from django.core.exceptions import ValidationError
from .models import InboxMessage

@receiver(user_signed_up)
def set_user_type_on_signup(sender, request, user, **kwargs):
    """
    Signal handler to set user type on signup.
    Triggers when a user signs up.
    
    Args:
        sender: The model class sending the signal
        request: The HTTP request object
        user: The user who signed up
        **kwargs: Additional keyword arguments
    """
    if not user.user_type:
        user.user_type = None
        user.save()
        messages.info(request, "Please set your account type.")


@receiver(user_logged_in)
def redirect_to_set_user_type(sender, request, user, **kwargs):
    """
    Signal handler to redirect user to set user type page if user doesn't have a user type.
    Triggers when a user logs in.
    
    Args:
        sender: The model class sending the signal
        request: The HTTP request object
        user: The user who logged in
        **kwargs: Additional keyword arguments
    """
    if not user.user_type:
        messages.info(request, "Please set your account type.")
        return redirect('set_user_type')
    
@receiver(social_account_added)
def set_user_type_on_social_signup(sender, request, sociallogin, **kwargs):
    """
    Signal handler to set user type on social signup.
    Triggers when a user signs up with a social account.
    
    Args:
        sender: The model class sending the signal
        request: The HTTP request object
        sociallogin: The social login object
        **kwargs: Additional keyword arguments
    """
    user = sociallogin.user
    if not user.user_type:
        user.user_type = None
        user.save()
        request.session['redirect_to_set_user_type'] = True

@receiver(user_signed_up)
def handle_user_signup(sender, request, user, **kwargs):
    """
    Signal handler to handle user signup.
    Triggers when a user signs up.
    
    Args:
        sender: The model class sending the signal
        request: The HTTP request object
        user: The user who signed up
        **kwargs: Additional keyword arguments
    """
    # Set default profile picture
    if not user.profile_picture:
        user.set_default_profile_picture()
    
    if not user.user_type:
        user.user_type = None
        user.save()
        messages.info(request, "Please complete your profile setup.")

