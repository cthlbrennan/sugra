from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class ProfileSetupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            if not self.is_profile_complete(request.user) and not self.is_exempt_url(request.path):
                messages.warning(request, "Please complete your profile setup before continuing.")
                return redirect('set_user_type')
        return self.get_response(request)

    def is_profile_complete(self, user):
        return user.user_type and user.has_usable_password() and user.username != f"user_{user.socialaccount_set.first().uid}"

    def is_exempt_url(self, path):
        exempt_urls = [
            reverse('set_user_type'),
            reverse('account_logout'),
            reverse('about')
        ]
        return path in exempt_urls