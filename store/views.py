from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from allauth.account.views import SignupView
from .forms import CustomSignupForm, UserTypeForm
from .decorators import gamer_required, developer_required


# Create your views here.

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

@login_required
def set_user_type(request):
    user = request.user
    if user.user_type:
        return redirect('gamer_dashboard' if user.user_type == 'gamer' else 'developer_dashboard')
    
    if request.method == 'POST':
        form = UserTypeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User type set successfully!")
            return redirect('gamer_dashboard' if user.user_type == 'gamer' else 'developer_dashboard')
    else:
        form = UserTypeForm(instance=user)
    
    return render(request, 'set_user_type.html', {'form': form})

def login_redirect(request):
    if request.user.is_authenticated:
        if not request.user.user_type:
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