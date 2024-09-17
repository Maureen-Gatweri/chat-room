from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.conf import settings
from django.shortcuts import render, get_object_or_404
import requests
import pika
import json
from django.http import JsonResponse
from datetime import timedelta
from django.utils.timezone import now
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Invitation, ChatRoom, ChatMessage
from django.views.decorators.csrf import csrf_exempt
from channels.generic.websocket import WebsocketConsumer

class CustomAuthenticatedView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]


class ChatMessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        room_name = request.query_params.get('room_name')
        if not room_name:
            return Response({'error': 'room_name parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        chat_room = get_object_or_404(ChatRoom, name=room_name)
        messages = ChatMessage.objects.filter(room=chat_room).order_by('timestamp')
        messages_data = [
            {
                'user': message.user.username,
                'message': message.content,
                'timestamp': message.timestamp.isoformat()
            }
            for message in messages
        ]
        return Response({'messages': messages_data}, status=status.HTTP_200_OK)

    def post(self, request):
        message_content = request.data.get('message')
        room_name = request.data.get('room_name')
        if not message_content or not room_name:
            return Response({'error': 'message and room_name are required'}, status=status.HTTP_400_BAD_REQUEST)

        chat_room = get_object_or_404(ChatRoom, name=room_name)
        message = ChatMessage.objects.create(room=chat_room, user=request.user, content=message_content)

        message_data = {
            'user': request.user.username,
            'message': message_content,
            'timestamp': message.timestamp.isoformat(),
            'room_name': room_name
        }

        self.publish_message(message_data)
        return Response(message_data, status=status.HTTP_201_CREATED)

    def publish_message(self, message):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()
            channel.queue_declare(queue='chat_messages')
            channel.basic_publish(exchange='', routing_key='chat_messages', body=json.dumps(message))

            room_group_name = f'chat_{message["room_name"]}'
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {'type': 'chat_message', 'message': message}
            )
            connection.close()
        except Exception as e:
            print(f"Error publishing message to RabbitMQ: {e}")


class MediaUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        if file:
            file_path = f'media/uploads/{file.name}'
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            return Response({'status': 'Media uploaded successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)


class NotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'notifications': []}, status=status.HTTP_200_OK)


class LeaveChatRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        room_name = request.data.get('room_name')
        if not room_name:
            return Response({'error': 'room_name is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        chat_room = get_object_or_404(ChatRoom, name=room_name)
        chat_room.users.remove(user)
        return Response({'status': 'Left chat room successfully'}, status=status.HTTP_200_OK)


class SendInvitationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        phone_number = request.data.get('phone_number')
        user = request.user

        if not all([first_name, last_name, phone_number]):
            return Response({'error': 'First name, last name, and phone number are required'}, status=status.HTTP_400_BAD_REQUEST)

        invitation = Invitation.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            invited_by=user
        )

        expiry_date = now() + timedelta(days=2)
        invitation.expires_at = expiry_date
        invitation.save()

        expiry_date_formatted = expiry_date.strftime("%Y-%m-%d %H:%M:%S")
        join_url = f"{settings.BASE_URL}/join/?invited_by={user.username}&phone_number={phone_number}"

        message = f"Hello {first_name} {last_name}, you've been invited to join Shawazi by {user.username}. This invitation expires on {expiry_date_formatted}. Click here to join: {join_url}"

        sms_response = self.send_sms(phone_number, message)

        if 'error' in sms_response:
            return Response({'status': 'Invitation created, but SMS failed', 'sms_response': sms_response}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'status': 'Invitation created and SMS sent', 'sms_response': sms_response, 'expires_at': expiry_date_formatted}, status=status.HTTP_200_OK)

    def send_sms(self, phone_number, message):
        headers = {
            "Authorization": f"Basic {settings.SMSLEOPARD_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "source": "Akirachix",
            "message": message,
            "destination": [{"number": phone_number}],
        }
        try:
            response = requests.post(settings.SMSLEOPARD_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}


def test_ui(request):
    return render(request, 'index.html')


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        self.send(text_data=json.dumps({
            'message': f"WebSocket connection established for room {self.room_name}."
        }))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'message': message
        }))


@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            return JsonResponse({'status': 'Message received successfully'}, status=200)
        return JsonResponse({'error': 'No message provided'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=400)


def get_messages(request):
    return JsonResponse({'messages': []}, status=200)

