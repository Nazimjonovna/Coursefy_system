from django.urls import path, re_path
from .consumers import ChatConsumer, ChatListConsumer, UserOnlineStatus


websocket_urlpatterns = [
    path('chat/', ChatConsumer.as_asgi()),
    path('chat-list/', ChatListConsumer.as_asgi()),
    path('chat/online/<int:pk>/', UserOnlineStatus.as_asgi())
    # re_path(r'^chat/(?P<chat_id>\w+)/$', ChatConsumer.as_asgi()),
    # re_path(r"^chat/$", ChatConsumer.as_asgi()),
]