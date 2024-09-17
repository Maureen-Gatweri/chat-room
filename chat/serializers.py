from rest_framework import serializers
from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'user', 'content', 'timestamp']
        read_only_fields = ['user', 'timestamp']