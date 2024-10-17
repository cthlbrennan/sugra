from django.shortcuts import render
from django.contrib import messages
from allauth.account.views import SignupView
from .forms import CustomSignupForm
from .decorators import gamer_required, developer_required


# Create your views here.

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

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