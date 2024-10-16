from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('gamer/dashboard/', views.gamer_dashboard, name='gamer_dashboard'),  # Add gamer dashboard URL
    path('developer/dashboard/', views.developer_dashboard, name='developer_dashboard'),  # Add developer dashboard URL
]