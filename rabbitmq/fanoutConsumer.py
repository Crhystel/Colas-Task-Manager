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

    os.makedirs('logs', exist_ok=True)

    def callback(ch, method, properties, body):
        mensaje = body.decode()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[Fanout] Mensaje recibido: {mensaje}")

        with open("logs/fanout.log", "a") as log:
            log.write(f"[{timestamp}] {mensaje}\n")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print("[*] Esperando anuncios generales (fanout). Ctrl+C para salir.")
    channel.start_consuming()
