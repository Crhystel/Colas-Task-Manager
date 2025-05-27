import pika
from config import settings
import os
from datetime import datetime
import json

def startDirectConsumer(usuario):
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        credentials=credentials
    ))
    channel = connection.channel()

    channel.exchange_declare(exchange=settings.EXCHANGE_DIRECT, exchange_type='direct')
    result = channel.queue_declare(queue=f"direct_{usuario}", durable=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=settings.EXCHANGE_DIRECT, queue=queue_name, routing_key=usuario)

    baseDir = os.path.dirname(os.path.abspath(__file__))
    logsDir = os.path.join(baseDir, "..", "logs")
    taskDir = os.path.join(baseDir, "..", "tasks")

    os.makedirs(logsDir, exist_ok=True)
    os.makedirs(taskDir, exist_ok=True)

    def callback(ch, method, properties, body):
        msgJson = body.decode()
        data=json.loads(msgJson)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[Direct] {usuario} recibió tarea.\n")

        with open(os.path.join(taskDir, f"{usuario}.txt"), "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] Tarea: {data['titulo']} - {data['contenido']}\n")
        with open(os.path.join(logsDir, f"direct_{usuario}.log"), "a", encoding="utf-8") as log:
            log.write(f"[{timestamp}] Tarea recibida: {msgJson}\n")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
