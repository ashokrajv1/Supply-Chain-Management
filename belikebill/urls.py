from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home,name='Bill-home'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('reg/',views.register,name='reg'),
    path('billing/',views.billing,name='billing'),
    path('inventory/',views.inventory,name='inventory'),
    path('addsupplier/',views.addsupplier,name='addsupplier'),
]
