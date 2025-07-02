import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import Message
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async


class ChatConsumers(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        my_username = self.scope['user'].username

        username = sorted([my_username, self.username])
        self.room_group_name = f'chat_{username[0]}_{username[1]}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = self.scope['user']
        receiver_username = self.username
        User = get_user_model()
        receiver = await database_sync_to_async(User.objects.get)(username=receiver_username)

        await database_sync_to_async(Message.objects.create)(
            sender=sender,
            receiver=receiver,
            text=message
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender.id
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id
        }))
