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
         # Log received data
        
        # Get status from incoming data, default to 'sent'
        status = text_data_json['status']
        print(text_data_json)
        
        if 'audio_url' in text_data_json:
            audio_url = text_data_json['audio_url']
            sender_username = text_data_json["username"]
            recipient_username = text_data_json["recipient"]
            print(recipient_username," - audio")

            if recipient_username:
                # Save the message with status
                await self.save_message(sender_username, recipient_username, audio_url, is_audio=True, status=status)

            # Send the audio message over the WebSocket
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_message",
                    "audio_url": audio_url,
                    "username": sender_username,
                    "receiver": recipient_username,
                    "status": status
                }
            )

        if 'message' in text_data_json:
            message = text_data_json["message"]
            sender_username = text_data_json["username"]
            recipient_username = text_data_json["receiver"]
            print(recipient_username," - message")

            if recipient_username:
                # Save the message and get the message object to obtain its ID
                message_obj = await self.save_message(sender_username, recipient_username, message, status=status)
                
                # Send the message over the WebSocket with its ID and status
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "send_message",
                        "message": message,
                        "username": sender_username,
                        "receiver": recipient_username,
                        "status": status  # Include status
                    }
                )

        if 'update' in text_data_json:
            sender_username = text_data_json['sender']
            receiver_username = text_data_json['receiver']
            status = text_data_json['status']

            print(f"Status update received: {status}")

            # Notify clients about the status update
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_message",
                    "username": sender_username,
                    "receiver": sender_username,
                    "status": status
                }
            )

    async def send_message(self, event):
        message = event.get("message", None)
        audio_url = event.get("audio_url", None)
        username = event["username"]
        receiver = event.get("receiver")
        message_id = event.get("message_id", None)
        status = event.get("status", 'sent')
        response = {
            "username": username,
            "receiver":receiver
        }

        if message:
            response["message"] = message
        if audio_url:
            response["audio_url"] = audio_url
        if message_id:
            response["message_id"] = message_id
        if status:
            response["status"] = status 

        await self.send(text_data=json.dumps(response))

    @database_sync_to_async
    def save_message(self, sender_username, recipient_username, content, is_audio=False,status='sent'):
        sender = User.objects.get(username=sender_username)
        recipient = User.objects.get(username=recipient_username)
        if is_audio:
            message = Message.objects.create(sender=sender, recipient=recipient, audio_url=content,status=status)
        else:
            message = Message.objects.create(sender=sender, recipient=recipient, content=content,status=status)
        
        return message  # Ensure the created message is returned