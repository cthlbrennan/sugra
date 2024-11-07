from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email
from allauth.account.models import EmailAddress

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Store cart before social login
        old_cart = request.session.get('cart', {})
        
        email = user_email(sociallogin.user)
        if email:
            try:
                user = EmailAddress.objects.get(email=email).user
                sociallogin.connect(request, user)
                # Restore cart after social login
                if old_cart:
                    request.session['cart'] = old_cart
            except EmailAddress.DoesNotExist:
                pass

        # Set temporary username for new users
        if not sociallogin.user.pk:  # Check pk instead of id
            sociallogin.user.username = f"user_{sociallogin.account.uid}"
            sociallogin.user.user_type = None

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        if not user.user_type:
            request.session['redirect_to_set_user_type'] = True
        return user