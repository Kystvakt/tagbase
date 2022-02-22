# urls.py
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'tagbase'

urlpatterns = [
    path('main/', views.main, name='main'),
    path('search/<str:keyword>/', views.search, name='search'),
]
