from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path('ws/chat/<str:username>/', consumers.ChatConsumers.as_asgi()),
]
