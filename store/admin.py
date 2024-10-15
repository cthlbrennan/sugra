from django.contrib import admin
from .models import User, Game, Wishlist, Order, OrderLine, Review, Screenshot, Message

# Register your models here.

admin.site.register(User)
admin.site.register(Game)
admin.site.register(Wishlist)
admin.site.register(Order)
admin.site.register(OrderLine)
admin.site.register(Review)
admin.site.register(Screenshot)
admin.site.register(Message)