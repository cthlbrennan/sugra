from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        if not user.id:
            # This is a new social account
            user.user_type = None
            user.username = f"user_{sociallogin.account.uid}"  # Temporary username
            messages.info(request, "Please set your account details.")

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        if not user.user_type:
            request.session['redirect_to_set_user_type'] = True
        return user