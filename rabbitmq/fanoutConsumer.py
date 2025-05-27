import pika
from config import settings
import os
from datetime import datetime

def startFanoutConsumer():
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        credentials=credentials
    ))
    channel = connection.channel()

    channel.exchange_declare(exchange=settings.EXCHANGE_FANOUT, exchange_type='fanout')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=settings.EXCHANGE_FANOUT, queue=queue_name)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(base_dir, "..", "logs")
    os.makedirs(logs_dir, exist_ok=True)

    def callback(ch, method, properties, body):
        mensaje = body.decode()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("[Fanout] Mensaje recibido.")

        with open(os.path.join(logs_dir, "fanout.log"), "a", encoding="utf-8") as log:
            log.write(f"[{timestamp}] {mensaje}\n")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
