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
        print('Received data:', text_data_json)  # Log received data

        if 'audio_url' in text_data_json:
            audio_url = text_data_json['audio_url']
            sender_username = text_data_json["username"]
            recipient_username = text_data_json.get("recipient")

            if recipient_username:
                await self.save_message(sender_username, recipient_username, audio_url, is_audio=True)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_message",
                    "audio_url": audio_url,
                    "username": sender_username,
                }
            )
        else:
            message = text_data_json["message"]
            sender_username = text_data_json["username"]
            recipient_username = text_data_json.get("recipient")

            if recipient_username:
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
        message = event.get("message", None)
        audio_url = event.get("audio_url", None)
        username = event["username"]

        response = {
            "username": username,
        }

        if message:
            response["message"] = message
        if audio_url:
            response["audio_url"] = audio_url

        await self.send(text_data=json.dumps(response))

    @database_sync_to_async
    def save_message(self, sender_username, recipient_username, content, is_audio=False):
        sender = User.objects.get(username=sender_username)
        recipient = User.objects.get(username=recipient_username)
        if is_audio:
            Message.objects.create(sender=sender, recipient=recipient, audio_url=content)
        else:
            Message.objects.create(sender=sender, recipient=recipient, content=content)
