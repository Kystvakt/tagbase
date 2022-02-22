# urls.py
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('main/', views.main),
    path('search/<str:keyword>/', views.search),
]
