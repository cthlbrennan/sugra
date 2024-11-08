from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class ProfileSetupMiddleware:
    """
    Middleware to ensure users complete their profile setup before accessing the site.
    
    Features:
    - Redirects incomplete profiles to setup page
    - Handles both regular and social auth users
    - Exempts specific URLs from redirection
    - Shows warning messages to guide users
    """

    def __init__(self, get_response):
        """
        Initialize middleware with Django's response handler.
        
        Args:
            get_response: Django's response handler function
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process each request through the middleware.
        
        Args:
            request: The HTTP request object
            
        Returns:
            HttpResponse: Either a redirect to profile setup or the normal response
        """
        # Only check authenticated non-superuser requests
        if request.user.is_authenticated and not request.user.is_superuser:
            # Check if profile is incomplete and URL is not exempt
            if not self.is_profile_complete(request.user) and not self.is_exempt_url(request.path):
                messages.warning(request, "Please complete your profile setup before continuing.")
                return redirect('set_user_type')
        return self.get_response(request)

    def is_profile_complete(self, user):
        """
        Check if a user's profile setup is complete.
        
        Args:
            user: The User object to check
            
        Returns:
            bool: True if profile is complete, False otherwise
            
        Notes:
            - For social auth users, checks if temporary username is still in use
            - For all users, checks for user type and password setup
        """
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
        """
        Check if the current URL should bypass profile completion check.
        
        Args:
            path: The current request path
            
        Returns:
            bool: True if URL is exempt, False otherwise
        """
        exempt_urls = [
            reverse('set_user_type'),
            reverse('account_logout'),
        ]
        return path in exempt_urls