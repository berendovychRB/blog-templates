from django.contrib import admin
from django.urls import path

from .views import *

urlpatterns = [
    path('detail/<int:id>/', comment_thread, name='thread'),
    path('<int:id>/delete/', comment_delete, name='delete'),
]
