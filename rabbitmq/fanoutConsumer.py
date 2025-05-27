import pika
from config import settings
import os
from datetime import datetime

def startFanoutConsumer():
    # Conexión a RabbitMQ
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        credentials=credentials
    ))
    channel = connection.channel()

    # Configuración del exchange fanout y cola temporal
    channel.exchange_declare(exchange=settings.EXCHANGE_FANOUT, exchange_type='fanout')
    result = channel.queue_declare(queue='', exclusive=True)
    queueName = result.method.queue
    channel.queue_bind(exchange=settings.EXCHANGE_FANOUT, queue=queueName)

    logsDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
    os.makedirs(logsDir, exist_ok=True)

    # Al recibir mensaje, lo guarda en el log
    def callback(ch, method, properties, body):
        mensaje = body.decode()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("[Fanout] Mensaje recibido.")

        with open(os.path.join(logsDir, "fanout.log"), "a", encoding="utf-8") as log:
            log.write(f"[{timestamp}] {mensaje}\n")

    channel.basic_consume(queue=queueName, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
