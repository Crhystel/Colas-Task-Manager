# import pika
# from config import settings
# import json

# def sendTarea(usuario, mensaje):
#     # Conexión a RabbitMQ
#     credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
#     connection = pika.BlockingConnection(pika.ConnectionParameters(
#         host=settings.RABBITMQ_HOST,
#         credentials=credentials
#     ))
#     channel = connection.channel()

#     # Declaramos exchange directo
#     channel.exchange_declare(exchange=settings.EXCHANGE_DIRECT, exchange_type='direct')

#     # Aseguramos que la cola del destinatario exista
#     channel.queue_declare(queue=f"direct_{usuario}", durable=True)
#     channel.queue_bind(exchange=settings.EXCHANGE_DIRECT, queue=f"direct_{usuario}", routing_key=usuario)

#     # Enviar mensaje directamente sin volver a codificar
#     channel.basic_publish(
#         exchange=settings.EXCHANGE_DIRECT,
#         routing_key=usuario,
#         body=mensaje,  # No usamos .encode()
#         properties=pika.BasicProperties(content_type='application/json')
#     )
#     print(f"[x] Tarea enviada a {usuario}: {mensaje}")
#     connection.close()
