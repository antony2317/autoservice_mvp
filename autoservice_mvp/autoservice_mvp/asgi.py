import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application  # ← исправленный импорт

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autoservice_mvp.settings')
django.setup()

from chat import routing  # только после django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
