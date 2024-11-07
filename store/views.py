import os
from decimal import Decimal
from io import BytesIO
import stripe
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import requests
from django.core.validators import MinValueValidator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, update_session_auth_hash, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q, Avg, Count, F, Sum
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from allauth.account.views import SignupView, LoginView
from .forms import CustomSignupForm, UserTypeAndPasswordForm, GameForm, UserProfilePictureForm, UserBioForm
from .decorators import gamer_required, developer_required
from .models import InboxMessage, Game, Message, User, Screenshot, Order, OrderLine, Wishlist, Review

# Create your views here.

class CustomLoginView(LoginView):
    def form_valid(self, form):
        auth_login(self.request, form.user)
        user = self.request.user
        
        # Check if user needs to complete profile setup
        if not user.user_type or not user.has_usable_password():
            next_url = self.request.session.get('next')
            if next_url:
                # Keep the next URL in session for after profile setup
                return redirect('set_user_type')
            return redirect('set_user_type')
        
        cart = self.request.session.get('cart', {})
        if cart and not self.request.session.get('next'):
            return redirect('checkout')
        # User has completed profile setup
        next_url = self.request.session.get('next')
        if next_url:
            del self.request.session['next']
            return redirect(next_url)
            
        # Default redirects
        if user.is_superuser:
            return redirect('admin:index')
        elif user.user_type == 'gamer':
            return redirect('gamer_dashboard')
        elif user.user_type == 'developer':
            return redirect('developer_dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, "Login failed. Please check your credentials and try again.")
        return super().form_invalid(form)

def index(request):
    filter_type = request.GET.get('filter')
    
    # Get all published games
    games_list = Game.objects.filter(is_published=True)
    
    # Apply filters if requested
    if filter_type == 'highest_rated':
        games_list = games_list.annotate(
            avg_rating=Avg('review__rating'),
            review_count=Count('review')
        ).order_by(
            F('avg_rating').desc(nulls_last=True),  # Put null ratings last
            '-review_count'
        )
    # Keep existing filter logic
    elif filter_type == 'recent':
        games_list = games_list.order_by('-submitted_at')
    elif filter_type == 'price':
        games_list = games_list.order_by('price')
    # Default ordering remains chronological
    
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
    
    if request.method == 'POST':
        form = UserTypeAndPasswordForm(user, request.POST, request.FILES)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Profile setup completed successfully!")
            
            # Check for stored next URL
            next_url = request.session.get('next')
            if next_url:
                del request.session['next']
                return redirect(next_url)
                
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
    # Get all games the user has purchased through orders
    library_games = Game.objects.filter(
        orderline__order__customer=request.user,
        is_published=True
    ).distinct()
    
    # Get wishlist games if user has a wishlist
    try:
        wishlist_games = request.user.wishlist.games.filter(is_published=True)
    except:
        wishlist_games = []
    
    # Get recent orders
    orders = Order.objects.filter(customer=request.user).order_by('-submitted_at')[:5]
    
    # Get recommended games based on purchased game genres
    owned_genres = library_games.values_list('genre', flat=True).distinct()
    recommended_games = Game.objects.filter(
        genre__in=owned_genres,
        is_published=True
    ).exclude(
        orderline__order__customer=request.user
    ).distinct()[:3]
    
    context = {
        'library_games': library_games,
        'wishlist_games': wishlist_games,
        'orders': orders,
        'recommended_games': recommended_games,
    }
    
    return render(request, 'gamer_dashboard.html', context)

@developer_required
def developer_dashboard(request):
    published_games = Game.objects.filter(developer=request.user, is_published=True)
    unread_messages_count = InboxMessage.objects.filter(developer=request.user, is_read=False).count()
    games_awaiting_review = Game.objects.filter(developer=request.user, is_published=False)
    
    # Get recent sales (last 10) for all published games
    recent_sales = OrderLine.objects.filter(
        game__in=published_games
    ).select_related(
        'game', 'order'
    ).order_by(
        '-order__submitted_at'
    )[:10]
    
    # Calculate earnings breakdown by game
    earnings_by_game = OrderLine.objects.filter(
        game__in=published_games
    ).values(
        'game__title'
    ).annotate(
        total_sales=Count('orderline_id'),
        revenue=Sum('game__price')
    ).order_by('-revenue')
    
    # Calculate total earnings
    total_earnings = OrderLine.objects.filter(
        game__in=published_games
    ).aggregate(
        total=Sum('game__price')
    )['total'] or 0
    
    # Get all reviews for the developer's published games
    reviews = Review.objects.filter(
        game__in=published_games
    ).select_related('game', 'customer').order_by('-submitted_at')
    
    # Calculate total reviews and aggregate rating
    total_reviews = reviews.count()
    aggregate_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    if aggregate_rating:
        aggregate_rating = round(aggregate_rating, 1)
    
    # Paginate reviews
    paginator = Paginator(reviews, 3)
    page = request.GET.get('review_page', 1)
    
    try:
        recent_reviews = paginator.page(page)
    except PageNotAnInteger:
        recent_reviews = paginator.page(1)
    except EmptyPage:
        recent_reviews = paginator.page(paginator.num_pages)
    
    context = {
        'published_games': published_games,
        'unread_messages_count': unread_messages_count,
        'games_awaiting_review': games_awaiting_review,
        'total_sales': OrderLine.objects.filter(game__in=published_games).count(),
        'aggregate_rating': aggregate_rating,
        'total_reviews': total_reviews,
        'recent_reviews': recent_reviews,
        'recent_sales': recent_sales,
        'total_earnings': total_earnings,
        'earnings_by_game': earnings_by_game,
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
    str_game_id = str(game_id)
    
    # Check if user owns the game
    game_owned = False
    has_reviewed = False
    if request.user.is_authenticated:
        game_owned = OrderLine.objects.filter(
            order__customer=request.user, 
            game=game
        ).exists()
        has_reviewed = Review.objects.filter(
            customer=request.user,
            game=game
        ).exists()
    
    # Get related games based on genre and developer
    related_games = Game.objects.filter(
        Q(genre=game.genre) | Q(developer=game.developer),
        is_published=True
    ).exclude(game_id=game_id)[:3]
    
    context = {
        'game': game,
        'related_games': related_games,
        'game_owned': game_owned,
        'has_reviewed': has_reviewed,
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
    games_list = Game.objects.filter(developer=developer, is_published=True)
    
    paginator = Paginator(games_list, 6)  # Show 6 games per page
    page = request.GET.get('page')
    
    try:
        games = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        games = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        games = paginator.page(paginator.num_pages)
    
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
    games = Game.objects.filter(is_published=True)
    
    if filter_type == 'price':
        games = games.order_by('price')
    elif filter_type == 'recent':
        games = games.order_by('-created_at')
    elif filter_type == 'highest_rated':
        games = games.annotate(
            avg_rating=Avg('review__rating'),
            review_count=Count('review')
        ).order_by(
            F('avg_rating').desc(nulls_last=True),  # Put null ratings last
            '-review_count'
        )
    elif filter_type == 'popular':
        games = games.annotate(
            purchase_count=Count('orderline')
        ).order_by('-purchase_count')
    
    games_data = [{
        'game_id': game.game_id,
        'title': game.title,
        'description': game.description,
        'genre': game.get_genre_display(),
        'price': float(game.price),
        'thumbnail': game.get_thumbnail(),
        'avg_rating': game.get_average_rating(),
        'review_count': game.get_review_count()
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

@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        
        if user is not None:
            # Password is correct, proceed with deletion
            user.delete()
            logout(request)
            messages.success(request, 'Account successfully deleted.')
            return redirect('index')
        else:
            messages.error(request, 'Incorrect password. Account deletion failed.')
            return redirect('user_profile')
    
    return redirect('user_profile')

def view_cart(request):
    return render(request, 'cart.html')

from django.http import JsonResponse

def add_to_cart(request, game_id):
    """Add a game to the shopping cart"""
    game = get_object_or_404(Game, game_id=game_id)
    
    # Check if user already owns the game
    if OrderLine.objects.filter(order__customer=request.user, game=game).exists():
        message = f'You already own {game.title}!'
        success = False
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': success,
                'message': message
            })
        messages.error(request, message)
        return redirect('game_detail', game_id=game_id)
    
    cart = request.session.get('cart', {})
    
    # Add game to cart or update quantity
    if str(game_id) in cart:
        message = f'{game.title} is already in your cart!'
        success = False
    else:
        cart[str(game_id)] = 1
        message = f'Added {game.title} to your cart'
        success = True

    request.session['cart'] = cart
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': success,
            'message': message,
            'inCart': str(game_id) in cart,
            'price': float(game.price)
        })
    return redirect('game_detail', game_id=game_id)

def remove_from_cart(request, game_id):
    """Remove a game from the shopping cart"""
    try:
        cart = request.session.get('cart', {})

        if str(game_id) in cart:
            del cart[str(game_id)]
            request.session['cart'] = cart
            messages.success(request, "Game removed from cart")
        else:
            messages.error(request, "This game was not in your cart")

    except Exception as e:
        messages.error(request, f"Error removing game from cart: {str(e)}")

    return redirect('view_cart')

@gamer_required
def checkout(request):
    try:
        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        stripe_secret_key = settings.STRIPE_SECRET_KEY
        
        if not stripe_public_key or not stripe_secret_key:
            messages.error(request, "Stripe keys are not set. Please check your settings.")
            return redirect('view_cart')
            
        cart = request.session.get('cart', {})

        if not cart:
            messages.error(request, "Your cart is empty!")
            return redirect('view_cart')

        if request.method == 'POST':
            cart = request.session.get('cart', {})
            
            total = Decimal('0.00')
            cart_items = []
            for game_id, quantity in cart.items():
                game = get_object_or_404(Game, game_id=game_id)
                total += game.price
                cart_items.append({
                    'game': game,
                    'quantity': quantity,
                })

            if total < Decimal('0.50'):
                messages.error(request, "Total amount must be at least €0.50")
                return redirect('view_cart')

            stripe_total = round(total * 100)
            stripe.api_key = stripe_secret_key

            try:
                intent = stripe.PaymentIntent.create(
                    amount=stripe_total,
                    currency=settings.STRIPE_CURRENCY,
                )

                order = Order.objects.create(
                    customer=request.user,
                    total_price=total,
                    stripe_pid=intent.id,
                )

                for game_id, quantity in cart.items():
                    game = get_object_or_404(Game, game_id=game_id)
                    OrderLine.objects.create(
                        order=order,
                        game=game,
                        price=game.price,
                    )

                request.session['cart'] = {}
                return redirect('checkout_success', order.order_id)

            except stripe.error.StripeError as e:
                messages.error(request, f"Payment error: {str(e)}")
                return redirect('checkout')

        else:
            total = Decimal('0.00')
            cart_items = []
            for game_id, quantity in cart.items():
                game = get_object_or_404(Game, game_id=game_id)
                total += game.price
                cart_items.append({
                    'game': game,
                    'quantity': quantity,
                })

            if total < Decimal('0.50'):
                messages.error(request, "Total amount must be at least €0.50")
                return redirect('view_cart')

            stripe_total = round(total * 100)
            stripe.api_key = stripe_secret_key

            try:
                intent = stripe.PaymentIntent.create(
                    amount=stripe_total,
                    currency=settings.STRIPE_CURRENCY,
                )
            except stripe.error.StripeError as e:
                messages.error(request, f"Error creating payment intent: {str(e)}")
                return redirect('view_cart')

            context = {
                'cart_items': cart_items,
                'total': total,
                'stripe_public_key': stripe_public_key,
                'client_secret': intent.client_secret,
            }

            return render(request, 'checkout.html', context)
            
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('view_cart')

@gamer_required
def checkout_success(request, order_id):
    """
    Handle successful checkouts
    """
    order = get_object_or_404(Order, order_id=order_id)
    
    if request.user != order.customer:
        messages.error(request, "You do not have permission to view this order.")
        return redirect('view_cart')

    # Send order confirmation email
    customer_email = order.customer.email
    subject = f'Sugra - Order Confirmation #{order.order_id}'
    current_site = get_current_site(request)
    # Render email text
    email_context = {
        'order': order,
        'current_site': current_site,
    }
    
    email_text = render_to_string(
        'account/email/order_confirmation_email.txt',
        email_context
    )
    
    # Send the email
    send_mail(
        subject,
        email_text,
        settings.DEFAULT_FROM_EMAIL,
        [customer_email],
        fail_silently=False,
    )

    messages.success(request, f'Order successfully processed! \
        Your order number is {order.order_id}. A confirmation \
        email has been sent to {customer_email}.')

    if 'cart' in request.session:
        del request.session['cart']

    context = {
        'order': order,
    }

    return render(request, 'checkout_success.html', context)

def handler404(request, exception):
    """Custom 404 page"""
    return render(request, '404.html', status=404)

def handler500(request):
    """Custom 500 page"""
    return render(request, '500.html', status=500)

def test_404(request):
    """Test view for 404 page"""
    return handler404(request, Exception())

def test_500(request):
    """Test view for 500 page"""
    return handler500(request)

@gamer_required
def library(request):
    games_list = Game.objects.filter(
        orderline__order__customer=request.user
    ).distinct().order_by('-orderline__order__submitted_at')
    
    paginator = Paginator(games_list, 9)  # Show 9 games per page
    page = request.GET.get('page')
    library_games = paginator.get_page(page)
    
    context = {
        'library_games': library_games,
    }
    return render(request, 'library.html', context)

@gamer_required
def download_game_thumbnail(request, game_id):
    game = get_object_or_404(Game, game_id=game_id)
    
    # Check if user has purchased the game
    if not OrderLine.objects.filter(order__customer=request.user, game=game).exists():
        messages.error(request, "You don't own this game.")
        return redirect('library')
    
    # Get the image from Cloudinary URL
    response = requests.get(game.get_thumbnail())
    
    if response.status_code == 200:
        # Prepare the response with appropriate headers
        content_type = response.headers.get('content-type', 'application/octet-stream')
        file_extension = content_type.split('/')[-1]
        
        # Create the response with the image content
        response = HttpResponse(response.content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{game.title}_thumbnail.{file_extension}"'
        return response
    else:
        messages.error(request, "Could not download the image. Please try again later.")
        return redirect('library')

@gamer_required
def order_history(request):
    orders_list = Order.objects.filter(customer=request.user).order_by('-submitted_at')
    paginator = Paginator(orders_list, 10)  # Show 10 orders per page
    
    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    
    context = {
        'orders': orders,
    }
    return render(request, 'order_history.html', context)

@gamer_required
def wishlist(request):
    try:
        wishlist_games = request.user.wishlist.games.filter(is_published=True)
    except:
        wishlist_games = []
    
    paginator = Paginator(wishlist_games, 9)  # Show 9 games per page
    page = request.GET.get('page')
    
    try:
        games = paginator.page(page)
    except PageNotAnInteger:
        games = paginator.page(1)
    except EmptyPage:
        games = paginator.page(paginator.num_pages)
        
    context = {
        'wishlist_games': games
    }
    return render(request, 'wishlist.html', context)

@gamer_required
def add_to_wishlist(request, game_id):
    game = get_object_or_404(Game, game_id=game_id)
    
    # Check if user already owns the game
    if OrderLine.objects.filter(order__customer=request.user, game=game).exists():
        messages.error(request, f'You already own {game.title}!')
        return redirect('game_detail', game_id=game_id)
    
    # Get or create wishlist for user
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    # Check if game is already in wishlist
    if game in wishlist.games.all():
        messages.info(request, f'{game.title} is already in your wishlist!')
    else:
        wishlist.games.add(game)
        messages.success(request, f'Added {game.title} to your wishlist!')
    
    return redirect('game_detail', game_id=game_id)

@gamer_required
def remove_from_wishlist(request, game_id):
    game = get_object_or_404(Game, game_id=game_id)
    
    try:
        wishlist = request.user.wishlist
        if game in wishlist.games.all():
            wishlist.games.remove(game)
            messages.success(request, f'Removed {game.title} from your wishlist!')
        else:
            messages.info(request, f'{game.title} is not in your wishlist!')
    except Wishlist.DoesNotExist:
        messages.error(request, 'You do not have a wishlist!')
    
    # Redirect back to the referring page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@gamer_required
def add_review(request, game_id):
    game = get_object_or_404(Game, game_id=game_id)
    
    # Check if user owns the game
    if not OrderLine.objects.filter(order__customer=request.user, game=game).exists():
        messages.error(request, 'You must own this game to review it.')
        return redirect('game_detail', game_id=game_id)
    
    # Check if user already reviewed this game
    if Review.objects.filter(customer=request.user, game=game).exists():
        messages.error(request, 'You have already reviewed this game.')
        return redirect('game_detail', game_id=game_id)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')
        
        if 1 <= rating <= 5:  # Validate rating
            Review.objects.create(
                game=game,
                customer=request.user,
                rating=rating,
                comment=comment
            )
            messages.success(request, 'Your review has been submitted!')
        else:
            messages.error(request, 'Invalid rating value.')
            
    return redirect('game_detail', game_id=game_id)

@gamer_required
def edit_review(request, game_id, review_id):
    review = get_object_or_404(Review, review_id=review_id, customer=request.user)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')
        
        if 1 <= rating <= 5:
            review.rating = rating
            review.comment = comment
            review.save()
            messages.success(request, 'Your review has been updated!')
        else:
            messages.error(request, 'Invalid rating value.')
            
    return redirect('game_detail', game_id=game_id)

@gamer_required
def delete_review(request, game_id, review_id):
    if request.method == 'POST':
        review = get_object_or_404(Review, review_id=review_id, customer=request.user)
        review.delete()
        messages.success(request, 'Your review has been deleted.')
    
    return redirect('game_detail', game_id=game_id)

def faq_view(request):
    """
    Render the FAQ page
    """
    return render(request, 'faq.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

@login_required
def download_personal_data(request):
    """Generate and download PDF of user's personal data"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles matching website
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#F7B32B'),  # bright-yellow-color
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        spaceBefore=20,
        spaceAfter=12,
        textColor=colors.HexColor('#2D3142')  # main-text color
    )
    
    # Title
    elements.append(Paragraph("Sugra Games - Your Data", title_style))
    elements.append(Spacer(1, 12))
    
    # Personal Info Section
    elements.append(Paragraph("Personal Information", heading_style))
    elements.append(Spacer(1, 12))
    
    # Table styles matching website colors
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#2D3142')),  # main-bg-color
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#F7F7F2')),   # off-white-color
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (-1, -1), colors.HexColor('#F7F7F2')),  # off-white-color
        ('TEXTCOLOR', (1, 0), (-1, -1), colors.HexColor('#2D3142')),   # main-text color
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2D3142'))
    ])
    
    personal_data = [
        ["Username", request.user.username],
        ["Email", request.user.email],
        ["Account Type", request.user.user_type],
        ["Date Joined", request.user.date_joined.strftime("%d %B %Y")],
    ]
    t = Table(personal_data, colWidths=[200, 300])
    t.setStyle(table_style)
    elements.append(t)
    elements.append(Spacer(1, 20))

    if request.user.user_type == 'gamer':
        # Add Gamer specific data
        elements.append(Paragraph("Your Game Library", heading_style))
        elements.append(Spacer(1, 12))
        
        library_games = Game.objects.filter(
            orderline__order__customer=request.user,
            is_published=True
        ).distinct()
        
        if library_games:
            game_data = [["Game Title", "Developer", "Purchase Date"]]
            for game in library_games:
                purchase_date = game.orderline_set.filter(
                    order__customer=request.user
                ).first().order.submitted_at.strftime("%d %B %Y")
                game_data.append([
                    game.title,
                    game.developer.username,
                    purchase_date
                ])
            
            t = Table(game_data, colWidths=[200, 150, 150])
            t.setStyle(table_style)
            elements.append(t)
        else:
            elements.append(Paragraph("No games in library", styles['Normal']))
            
    else:  # developer
        elements.append(Paragraph("Your Published Games", heading_style))
        elements.append(Spacer(1, 12))
        
        published_games = Game.objects.filter(developer=request.user)
        if published_games:
            game_data = [["Game Title", "Price", "Publication Status"]]
            for game in published_games:
                game_data.append([
                    game.title,
                    f"€{game.price}",
                    "Published" if game.is_published else "Under Review"
                ])
            
            t = Table(game_data, colWidths=[200, 100, 200])
            t.setStyle(table_style)
            elements.append(t)
        else:
            elements.append(Paragraph("No published games", styles['Normal']))

    # Build PDF
    doc.build(elements)
    
    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=sugra_data_{timezone.now().strftime("%Y%m%d")}.pdf'
    
    return response