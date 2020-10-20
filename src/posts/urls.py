from django.contrib import admin
from django.urls import path

from .views import *

urlpatterns = [
    path('', post_list, name='home'),
    path('create/', post_create, name='create'),
    path('detail/<str:slug>/', post_detail, name='detail'),
    path('<str:slug>/edit/', post_update, name='update'),
    path('<str:slug>/delete/', post_delete, name='delete'),
]
