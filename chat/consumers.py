# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from django.contrib.auth.models import User
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs'].get('room_name', 'default')
        self.room_group_name = f"chat_{self.room_name}"

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
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        sender_username = text_data_json["username"]
        recipient_username = text_data_json.get("recipient")  # Optional for private chat

        if recipient_username:  # If recipient username is provided, it's a private chat
            await self.save_message(sender_username, recipient_username, message)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_message",
                "message": message,
                "username": sender_username,
            }
        )

    async def send_message(self, event):
        message = event["message"]
        username = event["username"]
        await self.send(text_data=json.dumps({
            "message": message,
            "username": username
        }))

    @database_sync_to_async
    def save_message(self, sender_username, recipient_username, content):
        sender = User.objects.get(username=sender_username)
        recipient = User.objects.get(username=recipient_username)
        Message.objects.create(sender=sender, recipient=recipient, content=content)
