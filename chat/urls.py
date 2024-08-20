from django.urls import path
from chat.views import ChatListView, MessageCreateView, MessageMarkAsRead, MessagesByChat


urlpatterns = [
    path('private-chat/list/', ChatListView.as_view()),
    path('private-chat/', MessagesByChat.as_view()),
    path('private-chat/message/', MessageCreateView.as_view()),
    path('private-chat/message/<int:pk>/', MessageMarkAsRead.as_view()),
]
