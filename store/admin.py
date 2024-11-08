from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Game, Wishlist, Order, OrderLine, Review, Screenshot, Message, InboxMessage

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """
    Admin configuration for Game model.
    Provides custom views and actions for game management, including:
    - Game approval workflow
    - Review system for unpublished games
    - Developer notification system
    """
    list_display = ('title', 'developer', 'is_published', 'price')
    list_filter = ('is_published', 'genre')
    search_fields = ('title', 'developer__username')
    actions = ['approve_games']

    def get_urls(self):
        """
        Extends admin URLs to include custom review games view.
        Returns:
            list: Combined default and custom admin URLs
        """
        urls = super().get_urls()
        custom_urls = [
            path('review_games/', self.admin_site.admin_view(self.review_games_view), name='review_games'),
        ]
        return custom_urls + urls

    def review_games_view(self, request):
        """
        Custom view for reviewing unpublished games.
        Handles both GET requests (displaying games) and POST requests (approving/rejecting games).
        
        Features:
        - Game approval with developer notification
        - Game rejection with feedback
        - Automatic cleanup of rejected games
        """
        # Get all unpublished games
        games_to_review = Game.objects.filter(is_published=False)
        
        if request.method == 'POST':
            action = request.POST.get('action')
            if action:
                action_type, game_id = action.split('_')
                try:
                    game = Game.objects.get(game_id=game_id)
                    criticism = request.POST.get(f'criticism_{game_id}', '')
                    
                    # Handle game approval
                    if action_type == 'approve':
                        game.is_published = True
                        game.save()
                        # Notify developer of approval
                        InboxMessage.objects.create(
                            developer=game.developer,
                            game_title=game.title,
                            content=f"Your game '{game.title}' was approved! It is now available for customers to purchase and review on the marketplace.",
                            status='approved'
                        )
                        self.message_user(request, f"Game '{game.title}' has been approved.", messages.SUCCESS)
                    
                    # Handle game rejection
                    elif action_type == 'reject':
                        message_content = f"Your game '{game.title}' has been rejected. Reasons: {criticism}"
                        # Notify developer of rejection with feedback
                        InboxMessage.objects.create(
                            developer=game.developer,
                            game_title=game.title,
                            content=message_content,
                            status='rejected'
                        )
                        game.delete()
                        self.message_user(request, f"Game '{game.title}' has been rejected and deleted.", messages.SUCCESS)
                except Game.DoesNotExist:
                    self.message_user(request, f"Game with ID {game_id} not found.", messages.ERROR)
            return redirect('admin:review_games')

        context = {
            'games': games_to_review,
            'title': 'Review Games',
        }
        return render(request, 'admin/review_games.html', context)

    def approve_games(self, request, queryset):
        """
        Bulk action to approve multiple games at once.
        """
        queryset.update(is_published=True)
        self.message_user(request, f"{queryset.count()} games were approved.")
    approve_games.short_description = "Approve selected games"

    def index(self, request, extra_context=None):
        """
        Customizes admin index page to show count of games pending review.
        """
        games_to_review = Game.objects.filter(is_published=False).count()
        extra_context = extra_context or {}
        extra_context['games_to_review'] = games_to_review
        return super().index(request, extra_context=extra_context)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin configuration for Message model.
    Provides interface for managing user messages with bulk actions.
    """
    list_display = ('user', 'content', 'timestamp', 'read')
    list_filter = ('read', 'timestamp')
    search_fields = ('user__username', 'content')
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        """
        Bulk action to mark multiple messages as read.
        """
        queryset.update(read=True)
    mark_as_read.short_description = "Mark selected messages as read"

# Register remaining models with default admin interface
admin.site.register(User)
admin.site.register(Wishlist)
admin.site.register(Order)
admin.site.register(OrderLine)
admin.site.register(Review)
admin.site.register(Screenshot)
admin.site.register(InboxMessage)