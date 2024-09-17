import pika
import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        channel_layer = get_channel_layer()
        room_name = message.get('room_name', 'default_room')
        async_to_sync(channel_layer.group_send)(
            f'chat_{room_name}',
            {
                'type': 'chat_message',
                'message': message.get('message', 'No message content')
            }
        )
    except json.JSONDecodeError:
        print(f"Received non-JSON message: {body}")

def start_rabbitmq_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='chat_messages')
    channel.basic_consume(queue='chat_messages', auto_ack=True, on_message_callback=callback)
    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    start_rabbitmq_consumer()
