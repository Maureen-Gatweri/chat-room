import pika
import json
import os
import sys

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f"Received message: {message}")
    except json.JSONDecodeError:
        print(f"Received non-JSON message: {body}")

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='chat_messages')

    channel.basic_consume(queue='chat_messages',
                          auto_ack=True,
                          on_message_callback=callback)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)