import pika
from config import settings
import os
from datetime import datetime

def startTopicConsumer(binding_key):
    # Conexión a RabbitMQ
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        credentials=credentials
    ))
    channel = connection.channel()

    # Configuración del exchange topic y cola con binding_key
    channel.exchange_declare(exchange=settings.EXCHANGE_TOPIC, exchange_type='topic', durable=True)
    result = channel.queue_declare(queue=f"topic_{binding_key.replace('.', '_')}", durable=True)
    queueName = result.method.queue
    channel.queue_bind(exchange=settings.EXCHANGE_TOPIC, queue=queueName, routing_key=binding_key)

    logsDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
    os.makedirs(logsDir, exist_ok=True)

    # Guarda el mensaje en un archivo específico según binding_key
    def callback(ch, method, properties, body):
        mensaje = body.decode()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[Topic] Mensaje recibido para '{binding_key}'.")

        filename = f"topic_{binding_key.replace('.', '_')}.log"
        with open(os.path.join(logsDir, filename), "a", encoding="utf-8") as log:
            log.write(f"[{timestamp}] {mensaje}\n")

    channel.basic_consume(queue=queueName, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
