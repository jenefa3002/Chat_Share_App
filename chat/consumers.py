import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
from .utils import save_message_to_file, MESSAGE_FILE_PATH

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None
        self.room_name = None

    async def connect(self):
        self.room_name = "public_chat"
        self.room_group_name = f"chat_{self.room_name}"
        logger.info(f"WebSocket connected: {self.channel_name}")
        with open(MESSAGE_FILE_PATH, 'r') as file:
            messages = json.load(file)

        # Send previous messages to the user when they join
        for message in messages:
            await self.send(text_data=json.dumps(message))
        # Join room group
        await self.accept()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):

        logger.info(f"WebSocket disconnected: {self.channel_name}")

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        logger.info(f"Message received: {text_data}")
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )
        message_data = {
            'username': username,
            'message': message,
            'timestamp': str(self.channel_name),  # Or use a proper timestamp
        }

        # Save message to JSON file
        save_message_to_file(message_data)

        # Send message to WebSocket (broadcast to other clients)
        await self.send(text_data=json.dumps({
            'username': username,
            'message': message,
        }))

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))


import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ScreenShareConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the screen share group
        self.room_group_name = "screen_share_group"

        # Add the user to the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the user from the group when they disconnect
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive screen share image from WebSocket and broadcast it to the group
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        image = text_data_json['image']

        # Send the image to all users in the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'screen_share_message',
                'image': image
            }
        )

    # Receive message from the group
    async def screen_share_message(self, event):
        image = event['image']

        # Send the screen share image to WebSocket
        await self.send(text_data=json.dumps({
            'image': image
        }))
