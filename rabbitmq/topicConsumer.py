import pika
from config import settings

def startTopicConsumer(binding_key):
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        credentials=credentials
    ))
    channel = connection.channel()

    channel.exchange_declare(exchange=settings.EXCHANGE_TOPIC, exchange_type='topic')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=settings.EXCHANGE_TOPIC, queue=queue_name, routing_key=binding_key)

    def callback(ch, method, properties, body):
        print(f"[Topic] ({binding_key}) recibió: {body.decode()}")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(f"[*] Esperando mensajes para patrón '{binding_key}'")
    channel.start_consuming()
