from django.shortcuts import render
from .decorators import gamer_required, developer_required  # Import your decorators

# Create your views here.

def index(request):
    return render(request, 'index.html')

@gamer_required
def gamer_dashboard(request):
    return render(request, 'gamer_dashboard.html')

@developer_required
def developer_dashboard(request):
    return render(request, 'developer_dashboard.html')