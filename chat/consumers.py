from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Message
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "public_chat"
        self.room_group_name = f"chat_{self.room_name}"

        # Join the room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        logger.info(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        file_url = text_data_json.get('file_url', None)

        # Save the message to the database (async method)
        await self.save_message(username, message, file_url)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'file_url': file_url,
            }
        )
        logger.info(f"Message received: {message}")

    @sync_to_async
    def save_message(self, username, message, file_url):
        user = User.objects.get(username=username)  # Get the user by username
        # Save the message in the database
        Message.objects.create(user=user, content=message, file=file_url)
        logger.info(f"Message saved: {message}")

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))


class ScreenShareConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Assign a unique group name for screen sharing
        self.room_group_name = "screen_share_group"

        # Join the screen share group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group when the user disconnects
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        # Receive screen data from the WebSocket and send it to the group
        text_data_json = json.loads(text_data)
        stream = text_data_json['stream']  # Assuming 'stream' is a base64 or similar stream data

        # Send the screen data to all users in the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'screen_share_message',
                'stream': stream,  # Sending the stream to the group
            }
        )

    async def screen_share_message(self, event):
        # Handle the incoming screen share message and send it to the WebSocket
        stream = event['stream']

        # Send the screen stream to WebSocket
        await self.send(text_data=json.dumps({
            'stream': stream
        }))

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        # Join the private chat group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info(f"WebSocket connected to {self.room_group_name}")

    async def disconnect(self, close_code):
        # Leave the private chat group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"WebSocket disconnected from {self.room_group_name}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        file_url = text_data_json.get('file_url', None)

        # Save the message to the database
        await self.save_message(username, message, file_url, self.room_name)

        # Send message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'file_url': file_url,
            }
        )
        logger.info(f"Message received: {message}")

    @sync_to_async
    def save_message(self, username, message, file_url, room_name):
        user = User.objects.get(username=username)
        Message.objects.create(user=user, content=message, file=file_url, room_name=room_name)

    async def chat_message(self, event):
        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'file_url': event.get('file_url'),
        }))