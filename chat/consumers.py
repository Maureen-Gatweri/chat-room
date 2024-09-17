import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q
from .models import ChatRoom, ChatMessage, User
from channels.layers import get_channel_layer
from rest_framework.serializers import ModelSerializer
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract room name from the URL route
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Add user to the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Remove user from the room group on disconnect
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Handle receiving messages from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = text_data_json['user']
        room = text_data_json['room']

        # Save message to the database asynchronously
        await self.save_message(room, user, message)

        # Send message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user
            }
        )

    # Handle sending messages to WebSocket
    async def chat_message(self, event):
        message = event['message']
        user = event['user']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user': user
        }))

    @sync_to_async
    def save_message(self, room_name, username, content):
        room = ChatRoom.objects.get(name=room_name)
        user = User.objects.get(username=username)
        ChatMessage.objects.create(room=room, user=user, content=content)

# Serializer for ChatMessage
class ChatMessageSerializer(ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'user', 'content', 'timestamp']





# from channels.generic.websocket import WebsocketConsumer
# import json

# @sio.event
# async def connect(sid, environ):

# @sio.event
# async def disconnect(sid):

# @sio.on('message')
# async def handle_message(sid, data):

# @sio.on('message')
# async def handle_message(sid, data):
#     result = await sync_to_async(process_message)(data)
#     await sio.emit('response', result)


# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.room_name = self.scope['url_route'][0][1]
#         self.room_group_name = f'chat_{self.room_name}'

#         self.accept()

#         self.join_room()

#     def join_room(self):
#         self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']

#         self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )

#     def chat_message(self, event):
#         message = event['message']
#         self.send(text_data=json.dumps({
#             'message': message
#         }))



# from channels.generic.websocket import WebsocketConsumer
# import json

# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()
#         self.send(text_data=json.dumps({
#             'message': "WebSocket connection established."
#         }))

#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#         self.send(text_data=json.dumps({
#             'message': f"Message received: {message}"
#         }))

#     def disconnect(self, close_code):
#         pass

# def chat_message(self, event):
#     self.send(text_data=json.dumps({
#         'message': event['message']
#     }))
