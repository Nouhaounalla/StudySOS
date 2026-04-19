import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Mark user online
        user = self.scope.get('user')
        if user and user.is_authenticated:
            await self.set_user_online(user, True)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        user = self.scope.get('user')
        if user and user.is_authenticated:
            await self.set_user_online(user, False)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        user = self.scope.get('user')

        if not user or not user.is_authenticated:
            return

        # Save message to DB
        msg_obj = await self.save_message(user, self.room_name, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': user.id,
                'sender_name': user.get_full_name(),
                'sender_initials': user.get_initials(),
                'timestamp': msg_obj.created_at.isoformat() if msg_obj else timezone.now().isoformat(),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, user, room_name, content):
        from apps.users.message_models import Message
        try:
            return Message.objects.create(sender=user, room_name=room_name, content=content)
        except Exception:
            return None

    @database_sync_to_async
    def set_user_online(self, user, status):
        from apps.users.models import User
        User.objects.filter(pk=user.pk).update(is_online=status)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close()
            return
        self.group_name = f'notifications_{user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event))
