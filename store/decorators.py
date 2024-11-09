from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def gamer_required(view_func):
    """
    Decorator that restricts view access to users with 'gamer' type only.
    Must be used after @login_required as it assumes authentication.

    Args:
        view_func: The view function to be decorated

    Returns:
        function: Wrapped view function that checks user type

    Example:
        @gamer_required
        @login_required
        def my_view(request):
            ...
    """
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Check if the authenticated user is a gamer
        if request.user.user_type == 'gamer':
            return view_func(request, *args, **kwargs)

        # If not a gamer, show error and redirect
        messages.error(
            request,
            "You're not authorized to visit that page."
        )
        return redirect('index')  # Redirect to the index page
    return _wrapped_view


def developer_required(view_func):
    """
    Decorator that restricts view access to users with 'developer' type only.
    Must be used after @login_required as it assumes authentication.

    Args:
        view_func: The view function to be decorated

    Returns:
        function: Wrapped view function that checks user type

    Example:
        @developer_required
        @login_required
        def my_view(request):
            ...
    """
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Check if the authenticated user is a developer
        if request.user.user_type == 'developer':
            return view_func(request, *args, **kwargs)

        # If not a developer, show error and redirect
        messages.error(
            request,
            "You're not authorized to visit that page."
        )
        return redirect('index')  # Redirect to the index page
    return _wrapped_view
