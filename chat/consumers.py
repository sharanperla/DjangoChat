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
        print('Received data:',status)
        
        if 'audio_url' in text_data_json:
            audio_url = text_data_json['audio_url']
            sender_username = text_data_json["username"]
            recipient_username = text_data_json.get("recipient")

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
                    "status": status
                }
            )

        elif 'message' in text_data_json:
            message = text_data_json["message"]
            sender_username = text_data_json["username"]
            recipient_username = text_data_json.get("recipient")

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
                        "message_id": message_obj.id,
                        "status": status  # Include status
                    }
                )

        elif 'message_id' in text_data_json and 'status' in text_data_json:
            message_id = text_data_json['message_id']
            status = text_data_json['status']
            print(status)
            await self.update_message_status(message_id, status)
            # Notify clients about the status update
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "update_message_status",
                    "message_id": message_id,
                    "status": status
                }
            )



    async def send_message(self, event):
        message = event.get("message", None)
        audio_url = event.get("audio_url", None)
        username = event["username"]
        message_id = event.get("message_id", None)
        status = event.get("status", 'sent')
        response = {
            "username": username,
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
    @database_sync_to_async
    def update_message_status(self, message_id, status):
        print(f"Updating message {message_id} to status {status}")
        try:
            message = Message.objects.get(id=message_id)
            print(message,'message from table')
            message.status = status
            message.save()
        except Message.DoesNotExist:
             print(f"Message with id {message_id} does not exist")