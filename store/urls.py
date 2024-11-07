from allauth.account.views import EmailVerificationSentView
from django.urls import path
from . import views
from store.views import CustomLoginView


urlpatterns = [
    path('', views.index, name='index'),
    path('gamer/dashboard/', views.gamer_dashboard, name='gamer_dashboard'),  
    path('developer/dashboard/', views.developer_dashboard, name='developer_dashboard'),
    path('about/', views.about, name='about'),
    path('accounts/signup/', views.CustomSignupView.as_view(), name='account_signup'),
    path("accounts/confirm-email/", EmailVerificationSentView.as_view(), name="account_email_verification_sent"),
    path('set-user-type/', views.set_user_type, name='set_user_type'),
    path('accounts/login/', CustomLoginView.as_view(), name='account_login'),
    path('publish-game/', views.publish_game, name='publish_game'),
    path('developer/inbox/', views.developer_inbox, name='developer_inbox'),
    path('developer/inbox/delete/<int:message_id>/', views.delete_inbox_message, name='delete_inbox_message'),
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),
    path('filter-games/', views.filter_games, name='filter_games'),
    path('contact/', views.contact, name='contact'),
    path('developer/<str:username>/', views.developer_profile, name='developer_profile'),
    path('search/', views.search_games, name='search_games'),
    path('profile/', views.user_profile, name='user_profile'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:game_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:game_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/<order_id>', views.checkout_success, name='checkout_success'),
    path('404/', views.test_404, name='handler404'),
    path('500/', views.test_500, name='handler500'),
    path('library/', views.library, name='library'),
    path('download-thumbnail/<int:game_id>/', views.download_game_thumbnail, name='download_game_thumbnail'),
    path('orders/', views.order_history, name='order_history'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add-to-wishlist/<int:game_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:game_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('game/<int:game_id>/review/', views.add_review, name='add_review'),
    path('game/<int:game_id>/review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('game/<int:game_id>/review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('faq/', views.faq_view, name='faq'),
]