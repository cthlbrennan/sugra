from django.dispatch import receiver
from django.contrib.auth import user_logged_in
from django.shortcuts import redirect
from allauth.account.signals import user_signed_up
from django.contrib import messages

@receiver(user_signed_up)
def set_user_type_on_signup(sender, request, user, **kwargs):
    user.user_type = None
    user.save()

@receiver(user_logged_in)
def redirect_to_set_user_type(sender, request, user, **kwargs):
    if not user.user_type:
        messages.info(request, "Please set your account type.")
        return redirect('set_user_type')