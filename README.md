![image](https://github.com/user-attachments/assets/6507a991-1b3c-45f3-b99d-21fddb4e9ec0)
Install Required Software

Python (3.8+ recommended)
Virtual Environment (venv or virtualenv)
Node.js (for WebSocket debugging, optional)
Redis (for WebSocket and asynchronous message handling)
Django Project Setup

Initialize a Django project:

django-admin startproject chat_project
cd chat_project
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install django channels channels_redis
Create a Django app:

python manage.py startapp chat
Database Setup

Use SQLite for development or PostgreSQL/MySQL for production.
Run migrations:
python manage.py migrate
Redis Setup

Install Redis on your system:
For Windows: Use Redis for Windows.
For Linux: Use the package manager (sudo apt install redis).
Start the Redis server:
redis-server
2. WebSocket Integration
Install Daphne for WebSocket Support

pip install daphne
Update Django Settings Add channels to INSTALLED_APPS and configure the ASGI application:

# settings.py
INSTALLED_APPS += ['channels']

ASGI_APPLICATION = 'chat_project.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
Create ASGI File Modify or create chat_project/asgi.py:

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})
Define WebSocket Routing Add a routing.py file in the chat app:

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/screenshare/', consumers.ScreenShareConsumer.as_asgi()),
]
Create WebSocket Consumers

Create ChatConsumer for messaging.
Create ScreenShareConsumer for screen casting.
