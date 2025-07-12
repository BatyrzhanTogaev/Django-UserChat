from django.urls import path
from .views import chat_view


urlpatterns = [
    path('', chat_view, name='chat_home'),
    path('<str:username>/', chat_view, name='chat'),
]
