import pika
from config import settings
import os
from datetime import datetime

def startTopicConsumer(binding_key):
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        credentials=credentials
    ))
    channel = connection.channel()

    channel.exchange_declare(exchange=settings.EXCHANGE_TOPIC, exchange_type='topic')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=settings.EXCHANGE_TOPIC, queue=queue_name, routing_key=binding_key)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(base_dir, "..", "logs")
    os.makedirs(logs_dir, exist_ok=True)

    def callback(ch, method, properties, body):
        mensaje = body.decode()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[Topic] Mensaje recibido para '{binding_key}'.")

        filename = f"topic_{binding_key.replace('.', '_')}.log"
        with open(os.path.join(logs_dir, filename), "a", encoding="utf-8") as log:
            log.write(f"[{timestamp}] {mensaje}\n")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
