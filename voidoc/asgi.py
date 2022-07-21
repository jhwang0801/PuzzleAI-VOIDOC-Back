import os
import videocalls.routing

from django.core.asgi import get_asgi_application
from channels.auth    import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voidoc.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            videocalls.routing.websocket_urlpatterns
        )
    ),
})