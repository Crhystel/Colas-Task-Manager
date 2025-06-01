import os
from dotenv import load_dotenv


load_dotenv()


RABBITMQ_HOST = 'localhost'  
RABBITMQ_PORT = 5672

RABBITMQ_USER = os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_DEFAULT_PASS')


EXCHANGE_FANOUT = 'exchange_anuncios'
EXCHANGE_DIRECT = 'exchange_tareas'
EXCHANGE_TOPIC = 'exchange_proyectos'

QUEUE_ANUNCIOS = 'cola_anuncios'
QUEUE_TAREAS = 'cola_tareas'
QUEUE_PROYECTOS = 'cola_proyectos'

# Azure Service Bus Settings
AZURE_SERVICE_BUS_SENDER_CONNECTION_STRING = os.getenv("AZURE_SERVICE_BUS_SENDER")
AZURE_SERVICE_BUS_RECEIVER_CONNECTION_STRING = os.getenv("AZURE_SERVICE_BUS_RECEIVER")
AZURE_QUEUE_NAME = os.getenv("AZURE_QUEUE_NAME", "tareas")
