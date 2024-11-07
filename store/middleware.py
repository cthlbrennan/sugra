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
        # Check if user has a social account
        social_account = user.socialaccount_set.first()
        
        # Basic checks for all users
        has_basic_info = user.user_type and user.has_usable_password()
        
        # Additional check only for social account users
        if social_account:
            return has_basic_info and user.username != f"user_{social_account.uid}"
        
        # For regular users, just check basic info
        return has_basic_info

    def is_exempt_url(self, path):
        exempt_urls = [
            reverse('set_user_type'),
            reverse('account_logout'),
        ]
        return path in exempt_urls