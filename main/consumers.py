import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import Message
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async


class ChatConsumers(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer для личного чата в реальном времени.

    Особенности:
    - Создаёт уникальную комнату между двумя пользователями.
    - Отправляет и принимает сообщения через WebSocket.
    - Сохраняет сообщения в базе данных асинхронно.
    """

    async def connect(self):
        """
        Вызывается при подключении пользователя к WebSocket.

        Создаёт группу канала для чата на основе
        username текущего пользователя и собеседника,
        чтобы сообщения отправлялись только участникам чата.
        """

        # Получаем имя собеседника из URL
        self.username = self.scope['url_route']['kwargs']['username']

        # Получаем имя текущего пользователя
        my_username = self.scope['user'].username

        # Создаём уникальное комнату, чтобы один чат был для пары пользователей
        username = sorted([my_username, self.username])
        self.room_group_name = f'chat_{username[0]}_{username[1]}'

        # Добавляем текущий канал в группу
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()  # Принимаем подключение

    async def disconnect(self, close_code):
        """
        Вызывается при отключении пользователя от WebSocket.
        Удаляет канал из группы.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Вызывается при получении сообщения от WebSocket клиента.

        Действия:
        - Распарсить сообщение.
        - Сохранить сообщение в БД.
        - Отправить сообщение всем участникам группы через канал.
        """
        data = json.loads(text_data)
        message = data['message']
        sender = self.scope['user']
        receiver_username = self.username

        # Получаем модель пользователя
        User = get_user_model()

        # Получаем объект получателя асинхронно
        receiver = await database_sync_to_async(
            User.objects.get)(username=receiver_username)

        # Сохраняем сообщение асинхронно
        await database_sync_to_async(Message.objects.create)(
            sender=sender,
            receiver=receiver,
            text=message
        )

        # Отправляем сообщение в группу, чтобы все участники получили
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',  # Указывает, какой метод вызвать
                'message': message,
                'sender_id': sender.id
            }
        )

    async def chat_message(self, event):
        """
        Метод для получения сообщений из группы и отправки их в WS клиента
        """
        message = event['message']
        sender_id = event['sender_id']

        # Отправляем JSON данные клиенту
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id
        }))
