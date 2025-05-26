import pika
from config import settings

def sendAnuncio(mensaje):
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        credentials=credentials
    ))
    channel = connection.channel()

    channel.exchange_declare(exchange=settings.EXCHANGE_FANOUT, exchange_type='fanout')
    channel.basic_publish(exchange=settings.EXCHANGE_FANOUT, routing_key='', body=mensaje.encode())
    print(f"[x] Anuncio enviado: {mensaje}")
    connection.close()
