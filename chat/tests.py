from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from .models import ChatRoom, Invitation, ChatMessage

class ChatAppTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.login(username='testuser', password='testpass') 

        self.chat_room = ChatRoom.objects.create(name='test_room')
        self.invitation_url = reverse('send_invitation')
        self.chat_message_url = reverse('chat_message_list_create')  
        self.leave_chat_room_url = reverse('leave_chat_room')
        self.media_upload_url = reverse('media_upload')
        self.notifications_url = reverse('notifications')

    def test_send_invitation(self):
        data = {
            'first_name': 'Maureen',
            'last_name': 'Mwendwa',
            'phone_number': '+254704264110'
        }
        response = self.client.post(self.invitation_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Invitation created and SMS sent', response.data['status'])

    def test_create_chat_message(self):
        data = {
            'room': self.chat_room.id,
            'message': 'Hello, Maureen!'
        }
        response = self.client.post(self.chat_message_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Hello, world!')

    def test_leave_chat_room(self):
        self.chat_room.users.add(self.user)
        data = {
            'room_name': 'test_room'
        }
        response = self.client.post(self.leave_chat_room_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Left chat room successfully', response.data['status'])

    def test_media_upload(self):
        response = self.client.post(self.media_upload_url, {'file': None})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'No file uploaded')

    def test_notifications_view(self):
        response = self.client.get(self.notifications_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['notifications'], [])
