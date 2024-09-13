from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.conf import settings
from django.shortcuts import get_object_or_404
import requests
import pika
import json

from .models import Invitation, ChatRoom, ChatMessage
from .serializers import ChatMessageSerializer

class CustomAuthenticatedView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

class ChatMessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            self.publish_message(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def publish_message(self, message):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()
            channel.queue_declare(queue='chat_messages')
            channel.basic_publish(exchange='', routing_key='chat_messages', body=json.dumps(message))
            connection.close()
        except Exception as e:
            print(f"Error publishing message to RabbitMQ: {e}")

class MediaUploadView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if file:
            return Response({'status': 'Media uploaded successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

class NotificationsView(APIView):
    def get(self, request):
        return Response({'notifications': []}, status=status.HTTP_200_OK)

class LeaveChatRoomView(APIView):
    def post(self, request):
        room_name = request.data.get('room_name')
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

        if not first_name or not last_name or not phone_number:
            return Response({'error': 'First name, last name, and phone number are required'}, status=status.HTTP_400_BAD_REQUEST)

        invitation = Invitation.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            invited_by=user
        )

        expiry_date = invitation.expires_at.strftime("%Y-%m-%d %H:%M:%S")
        join_url = f"http://shawazi.com/join/?invited_by={user.username}&phone_number={phone_number}"

        message = f"Hello {first_name} {last_name}, you've been invited to join Shawazi by {user.username}. This invitation expires on {expiry_date}. Click here to join: {join_url}"

        sms_response = self.send_sms(phone_number, message)

        if 'error' in sms_response:
            return Response({'status': 'Invitation created, but SMS failed', 'sms_response': sms_response}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'status': 'Invitation created and SMS sent', 'sms_response': sms_response}, status=status.HTTP_200_OK)

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