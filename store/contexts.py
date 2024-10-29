from decimal import Decimal
from django.shortcuts import get_object_or_404
from .models import Game

def cart_contents(request):
    cart_items = []
    total = 0
    game_count = 0
    cart = request.session.get('cart', {})

    for game_id, quantity in cart.items():
        game = get_object_or_404(Game, game_id=game_id)
        total += game.price
        game_count += quantity
        cart_items.append({
            'game': game,
            'quantity': quantity,
        })

    grand_total = total

    context = {
        'cart_items': cart_items,
        'total': total,
        'game_count': game_count,
        'grand_total': grand_total,
    }

    return context