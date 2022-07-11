from django.urls import path

from videocalls.consumers import VideoCallConsumer

websocket_urlpatterns = [
    path(r'ws/call/<str:room_name>', VideoCallConsumer.as_asgi())
]