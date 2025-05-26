import pika
from config import settings

def sendTarea(usuario, mensaje):
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        credentials=credentials
    ))
    channel = connection.channel()

    channel.exchange_declare(exchange=settings.EXCHANGE_DIRECT, exchange_type='direct')
    channel.basic_publish(exchange=settings.EXCHANGE_DIRECT, routing_key=usuario, body=mensaje.encode())
    print(f"[x] Tarea enviada a {usuario}: {mensaje}")
    connection.close()
