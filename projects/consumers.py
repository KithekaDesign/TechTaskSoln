import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import Message, Project


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code: int):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @sync_to_async
    def save_message(self, sender_id, project_id, message):

        project = Project.objects.get(id=project_id)  # type: ignore[attr-defined]
        from django.contrib.auth import get_user_model
        User = get_user_model()
        sender = User.objects.get(id=sender_id)

        Message.objects.create(  # type: ignore[attr-defined]
            sender=sender,
            project=project,
            content=message
        )

        return sender.username

    async def receive(self, text_data: str | None = None, bytes_data: bytes | None = None):  # type: ignore[override]

        if not text_data:
            return  # ignore binary or empty frames

        data = json.loads(text_data)

        message = data['message']
        sender_id = data['sender']
        project_id = data['project']

        # Save message in database and get sender username
        sender_username = await self.save_message(sender_id, project_id, message)

        # Send message to chat room — include sender info
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_username,
                'sender_id': sender_id,
            }
        )

    async def chat_message(self, event):

        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'sender_id': event['sender_id'],
        }))