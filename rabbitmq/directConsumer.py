# import pika
# from config import settings
# import os
# from datetime import datetime
# import json

# def startDirectConsumer(usuario):
#     # Conexión a RabbitMQ con autenticación
#     credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
#     connection = pika.BlockingConnection(pika.ConnectionParameters(
#         host=settings.RABBITMQ_HOST,
#         credentials=credentials
#     ))
#     channel = connection.channel()

#     # Configuración del exchange y la cola
#     channel.exchange_declare(exchange=settings.EXCHANGE_DIRECT, exchange_type='direct')
#     result = channel.queue_declare(queue=f"direct_{usuario}", durable=True)
#     queue_name = result.method.queue
#     channel.queue_bind(exchange=settings.EXCHANGE_DIRECT, queue=queue_name, routing_key=usuario)

#     # Directorios para tareas y logs
#     baseDir = os.path.dirname(os.path.abspath(__file__))
#     logsDir = os.path.join(baseDir, "..", "logs")
#     taskDir = os.path.join(baseDir, "..", "tasks")
#     os.makedirs(logsDir, exist_ok=True)
#     os.makedirs(taskDir, exist_ok=True)

#     # Acción al recibir mensaje
#     def callback(ch, method, properties, body):
#         try:
#             msgJson = body.decode()
#             data = json.loads(msgJson)

#             titulo = data.get("titulo", "Sin título")
#             contenido = data.get("contenido", "Sin contenido")

#             timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             print(f"\n[Direct] {usuario} recibió tarea.\n")

#             with open(os.path.join(taskDir, f"{usuario}.txt"), "a", encoding="utf-8") as f:
#                 f.write(f"[{timestamp}] Tarea: {titulo} - {contenido}\n")
#             with open(os.path.join(logsDir, f"direct_{usuario}.log"), "a", encoding="utf-8") as log:
#                 log.write(f"[{timestamp}] Tarea recibida: {msgJson}\n")

#         except Exception as e:
#             print(f"[!] Error procesando mensaje para {usuario}: {e}")
#             with open(os.path.join(logsDir, f"direct_{usuario}.log"), "a", encoding="utf-8") as log:
#                 log.write(f"[{datetime.now()}] Error: {e} - Raw: {body}\n")

#     channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
#     channel.start_consuming()
