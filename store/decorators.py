from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def gamer_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type == 'gamer':
            return view_func(request, *args, **kwargs)
        messages.error(request, "You're not authorized to visit that page.")
        return redirect('index')  # Redirect to the index page
    return _wrapped_view

def developer_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type == 'developer':
            return view_func(request, *args, **kwargs)
        messages.error(request, "You're not authorized to visit that page.")
        return redirect('index')  # Redirect to the index page
    return _wrapped_view