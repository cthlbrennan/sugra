import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from allauth.account.views import SignupView, LoginView
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q
from django.core.files.base import ContentFile
from .forms import CustomSignupForm, UserTypeAndPasswordForm, GameForm, UserProfilePictureForm, UserBioForm
from .decorators import gamer_required, developer_required
from .models import InboxMessage, Game, Message, User, Screenshot


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
    games_list = Game.objects.filter(is_published=True).order_by('-created_at')
    paginator = Paginator(games_list, 6)  # Show 6 games per page

    page = request.GET.get('page')
    try:
        games = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        games = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        games = paginator.page(paginator.num_pages)

    return render(request, 'index.html', {'games': games})

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
        form = UserTypeAndPasswordForm(user, request.POST, request.FILES)  # Added request.FILES here
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
    published_games = Game.objects.filter(developer=request.user, is_published=True)
    unread_messages_count = InboxMessage.objects.filter(developer=request.user, is_read=False).count()
    games_awaiting_review = Game.objects.filter(developer=request.user, is_published=False)
    context = {
        'published_games': published_games,
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
def delete_inbox_message(request, message_id):
    message = get_object_or_404(InboxMessage, message_id=message_id, developer=request.user)
    if request.method == 'POST':
        message.delete()
        messages.success(request, "Message deleted successfully.")
    return redirect('developer_inbox')

def game_detail(request, game_id):
    game = get_object_or_404(Game, game_id=game_id)
    
    # Get related games based on genre and developer
    related_games = Game.objects.filter(
        Q(genre=game.genre) | Q(developer=game.developer),
        is_published=True
    ).exclude(game_id=game_id)[:3]  # Limit to 3 games
    
    context = {
        'game': game,
        'related_games': related_games,
    }
    return render(request, 'game_detail.html', context)

class CustomSignupView(SignupView):
    form_class = CustomSignupForm

    def form_invalid(self, form):
        response = super(CustomSignupView, self).form_invalid(form)
        messages.error(self.request, "Signup failed. Please check the form and try again.")
        return response

    def form_valid(self, form):
        response = super(CustomSignupView, self).form_valid(form)
        user = self.user
        if not user.profile_picture:
            default_image_path = os.path.join(settings.STATIC_ROOT, 'images', 'default-profile-photo.png')
            with open(default_image_path, 'rb') as f:
                django_file = ContentFile(f.read())
                user.profile_picture.save('default-profile-photo.png', django_file, save=True)
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
            game.is_published = False
            game.save()

            # Handle screenshots
            for i in range(1, 4):
                screenshot = form.cleaned_data.get(f'screenshot{i}')
                if screenshot:
                    Screenshot.objects.create(
                        game=game,
                        image=screenshot,
                        alt_text=f"{game.title} Screenshot {i}"
                    )

            messages.success(request, "Your game has been submitted for review.")
            return redirect('developer_dashboard')
    else:
        form = GameForm()
    return render(request, 'publish_game.html', {'form': form})

@login_required
def contact(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(user=request.user, content=content)
            messages.success(request, "Your message has been sent.")
            if request.user.user_type == 'gamer':
                return redirect('gamer_dashboard')
            elif request.user.user_type == 'developer':
                return redirect('developer_dashboard')
    return render(request, 'contact.html')

def developer_profile(request, username):
    developer = get_object_or_404(User, username=username, user_type='developer')
    games = Game.objects.filter(developer=developer, is_published=True)
    context = {
        'developer': developer,
        'games': games,
    }
    return render(request, 'developer_profile.html', context)

def search_games(request):
    query = request.GET.get('query', '')
    games = Game.objects.filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query) |
        Q(genre__icontains=query)
    ).filter(is_published=True)
    
    context = {
        'games': games,
        'search_query': query
    }
    return render(request, 'index.html', context)

def filter_games(request):
    filter_type = request.GET.get('filter')
    if filter_type == 'price':
        games = Game.objects.filter(is_published=True).order_by('price')
    elif filter_type == 'recent':
        games = Game.objects.filter(is_published=True).order_by('-created_at')
    else:
        games = Game.objects.filter(is_published=True)
    
    games_data = [{
        'game_id': game.game_id,
        'title': game.title,
        'description': game.description,
        'genre': game.get_genre_display(),
        'price': float(game.price),
        'thumbnail': game.get_thumbnail()
    } for game in games]
    
    return JsonResponse(games_data, safe=False)

@login_required
def user_profile(request):
    bio_form = UserBioForm(instance=request.user)
    picture_form = UserProfilePictureForm(instance=request.user)

    if request.method == 'POST':
        if 'update_bio' in request.POST:
            bio_form = UserBioForm(request.POST, instance=request.user)
            if bio_form.is_valid():
                bio_form.save()
                messages.success(request, 'Your bio has been updated.')
        elif 'update_picture' in request.POST:
            picture_form = UserProfilePictureForm(request.POST, request.FILES, instance=request.user)
            if picture_form.is_valid():
                picture_form.save()
                messages.success(request, 'Your profile picture has been updated.')

    context = {
        'bio_form': bio_form,
        'picture_form': picture_form,
        'user': request.user
    }
    return render(request, 'user_profile.html', context)