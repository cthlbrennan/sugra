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

]