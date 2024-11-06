from django.contrib import admin
from django.urls import path, include
from store.views import login_redirect, CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls') ),
    path('accounts/', include('allauth.urls')),
    path('login-redirect/', login_redirect, name='login_redirect'),
    path('accounts/login/', CustomLoginView.as_view(), name='account_login'),
]

handler404 = 'store.views.handler404'
handler500 = 'store.views.handler500'
