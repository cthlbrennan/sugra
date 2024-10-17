from django.shortcuts import render
from .decorators import gamer_required, developer_required
from allauth.account.views import SignupView
from .forms import CustomSignupForm


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

    def form_valid(self, form):
        user = form.save(self.request)
        return redirect('account_login')  # Redirect to login or any other page after successful signup
