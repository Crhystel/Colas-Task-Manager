import pika
from config import settings
import os
from datetime import datetime

def startDirectConsumer(usuario):
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        credentials=credentials
    ))
    channel = connection.channel()

    channel.exchange_declare(exchange=settings.EXCHANGE_DIRECT, exchange_type='direct')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=settings.EXCHANGE_DIRECT, queue=queue_name, routing_key=usuario)

    os.makedirs('logs', exist_ok=True)
    os.makedirs('tareas', exist_ok=True)

    def callback(ch, method, properties, body):
        mensaje = body.decode()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[Direct] {usuario} recibió tarea: {mensaje}")

        with open(f"tareas/{usuario}.txt", "a") as f:
            f.write(f"[{timestamp}] {mensaje}\n")
        with open(f"logs/direct_{usuario}.log", "a") as log:
            log.write(f"[{timestamp}] Tarea recibida: {mensaje}\n")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(f"[*] {usuario} esperando tareas directas.")
    channel.start_consuming()
