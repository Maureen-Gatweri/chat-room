from django.urls import path
from .views import (
    CustomAuthenticatedView,
    SendInvitationView,
    ChatMessageListCreateView,
    MediaUploadView,
    NotificationsView,
    LeaveChatRoomView,
    # AcceptInvitationView
)
urlpatterns = [
    path ('send_invitation/', SendInvitationView.as_view(), name = 'send_invitation'),
    path('auth/',CustomAuthenticatedView.as_view(),name='custom_auth'),
    # path('accept-invitation/<int:invitation_id>/', AcceptInvitationView.as_view(), name='accept-invitation'),
    path('invite/', SendInvitationView.as_view(), name='send_invitation'),
    path('messages/', ChatMessageListCreateView.as_view(), name='chat_message_list_create'),
    path('media_upload/', MediaUploadView.as_view(), name='media_upload'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('leave_room/', LeaveChatRoomView.as_view(), name='leave_chatroom'),
    path('send-invitation/', SendInvitationView.as_view(), name='send_invitation'),

]   