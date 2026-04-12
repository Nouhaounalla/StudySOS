import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studysos.settings')

# Get HTTP application first
django_asgi_app = get_asgi_application()

# Now import Channels stuff (AFTER Django setup)
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.middleware import JWTAuthMiddleware
from chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})