from django.contrib import admin
from django.urls import path, re_path
from . import consumers, views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api/chat/messages/', views.ChatMessageListCreateView.as_view(), name='chat_message_list_create'),
    path('api/send_invitation/', views.SendInvitationView.as_view(), name='send_invitation'),
    path('api/auth/', views.CustomAuthenticatedView.as_view(), name='custom_auth'),
    path('api/messages/send/', views.send_message, name='send_message'), 
    path('api/messages/retrieve/', views.get_messages, name='get_messages'),  
    path('api/media_upload/', views.MediaUploadView.as_view(), name='media_upload'),
    path('notifications/', views.NotificationsView.as_view(), name='notifications'),
    path('leave_room/', views.LeaveChatRoomView.as_view(), name='leave_chatroom'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]

