import pika
from config import settings

def sendProyecto(routing_key, mensaje):
    # Conexión a RabbitMQ
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        credentials=credentials
    ))
    channel = connection.channel()

    # Exchange tipo topic: filtra por routing key
    channel.exchange_declare(exchange=settings.EXCHANGE_TOPIC, exchange_type='topic', durable=True)

    # Publicar mensaje
    channel.basic_publish(
        exchange=settings.EXCHANGE_TOPIC,
        routing_key=routing_key,
        body=mensaje,  # Quitamos .encode()
        properties=pika.BasicProperties(delivery_mode=2)  # persistente
    )
    print(f"[x] Proyecto enviado a {routing_key}: {mensaje}")
    connection.close()
