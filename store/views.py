from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from allauth.account.views import SignupView, LoginView
from .forms import CustomSignupForm, UserTypeAndPasswordForm, GameForm
from .decorators import gamer_required, developer_required
from django.urls import reverse  
from .models import InboxMessage, Game


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
    unread_messages_count = InboxMessage.objects.filter(developer=request.user, is_read=False).count()
    games_awaiting_review = Game.objects.filter(developer=request.user, is_published=False)
    context = {
        'unread_messages_count': unread_messages_count,
        'games_awaiting_review': games_awaiting_review,
    }
    return render(request, 'developer_dashboard.html', context)

@developer_required
def developer_inbox(request):
    inbox_messages = InboxMessage.objects.filter(developer=request.user).order_by('-created_at')
    context = {
        'inbox_messages': inbox_messages,
    }
    return render(request, 'developer_inbox.html', context)

@developer_required
def mark_inbox_message_read(request, message_id):
    if request.method == 'POST':
        message = get_object_or_404(InboxMessage, message_id=message_id, developer=request.user)
        message.is_read = True
        message.save()
    return redirect('developer_dashboard')

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

@developer_required
def publish_game(request):
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES)
        if form.is_valid():
            game = form.save(commit=False)
            game.developer = request.user
            game.is_published = False  # Set to False by default
            game.save()
            messages.success(request, "Your game has been submitted for review.")
            return redirect('developer_dashboard')
    else:
        form = GameForm()
    return render(request, 'publish_game.html', {'form': form})