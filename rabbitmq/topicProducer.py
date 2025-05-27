import pika
from config import settings

def sendProyecto(routing_key, mensaje):
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        credentials=credentials
    ))
    channel = connection.channel()

    channel.exchange_declare(exchange=settings.EXCHANGE_TOPIC, exchange_type='topic', durable=True)

    channel.basic_publish(exchange=settings.EXCHANGE_TOPIC, routing_key=routing_key, body=mensaje.encode())
    print(f"[x] Proyecto enviado a {routing_key}: {mensaje}")
    connection.close()
