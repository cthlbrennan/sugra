from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from allauth.account.views import SignupView, LoginView
from .forms import CustomSignupForm, UserTypeAndPasswordForm
from .decorators import gamer_required, developer_required
from django.urls import reverse  


# Create your views here.

class CustomLoginView(LoginView):
    def form_valid(self, form):
        auth_login(self.request, form.user)
        
        # Now that the user is logged in, we can access user attributes
        user = self.request.user
        
        if user.is_superuser:
            return redirect('admin:index')
        elif user.user_type:
            if user.user_type == 'gamer':
                return redirect('gamer_dashboard')
            elif user.user_type == 'developer':
                return redirect('developer_dashboard')
        else:
            messages.info(self.request, "Please set your account type.")
            return redirect('set_user_type')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, "Login failed. Please check your credentials and try again.")
        return super().form_invalid(form)

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

@login_required
def set_user_type(request):
    user = request.user
    if user.is_superuser:
        messages.info(request, "As an admin, you don't need to set a user type.")
        return redirect('admin:index')
    
    if user.user_type and user.has_usable_password() and not user.username.startswith("user_"):
        return redirect('gamer_dashboard' if user.user_type == 'gamer' else 'developer_dashboard')
    
    if request.method == 'POST':
        form = UserTypeAndPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Profile setup completed successfully!")
            return redirect('gamer_dashboard' if user.user_type == 'gamer' else 'developer_dashboard')
    else:
        initial_data = {'username': user.username if not user.username.startswith("user_") else ''}
        form = UserTypeAndPasswordForm(user, initial=initial_data)
    
    return render(request, 'set_user_type.html', {'form': form})

def login_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin:index')
        if not request.user.user_type or not request.user.has_usable_password() or request.user.username.startswith("user_"):
            return redirect('set_user_type')
        return redirect('gamer_dashboard' if request.user.user_type == 'gamer' else 'developer_dashboard')
    return redirect('account_login')

@gamer_required
def gamer_dashboard(request):
    return render(request, 'gamer_dashboard.html')

@developer_required
def developer_dashboard(request):
    return render(request, 'developer_dashboard.html')

class CustomSignupView(SignupView):
    form_class = CustomSignupForm

    def form_invalid(self, form):
        response = super(CustomSignupView, self).form_invalid(form)
        messages.error(self.request, "Signup failed. Please check the form and try again.")
        return response

    def form_valid(self, form):
        response = super(CustomSignupView, self).form_valid(form)
        messages.success(self.request, "Signup successful! Welcome to our site.")
        return response

    def get_success_url(self):
        user = self.user
        if user.user_type == 'gamer':
            return reverse('gamer_dashboard')
        elif user.user_type == 'developer':
            return reverse('developer_dashboard')
        else:
            return reverse('set_user_type')