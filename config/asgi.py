"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

# import os
# from django.core.asgi import get_asgi_application
# import django

# from config.middlewares import JWTAuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
# from chat.routing import websocket_urlpatterns

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# asgi_application = get_asgi_application()
# # django.setup()



# application = ProtocolTypeRouter(
#         {
#             "http": asgi_application,
#             "websocket": JWTAuthMiddlewareStack(
#                                 URLRouter(websocket_urlpatterns)
#                                 )
#         }
#     )


import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from config.middlewares import JWTAuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.routing import websocket_urlpatterns


application = ProtocolTypeRouter(
                                {
                                "http": get_asgi_application(),
                                "websocket": JWTAuthMiddlewareStack(
                                                                    URLRouter(websocket_urlpatterns)
                                                                    )
                                }
                                )
