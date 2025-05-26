import os
from dotenv import load_dotenv

load_dotenv()


RABBITMQ_HOST = 'rabbitmq'  
RABBITMQ_PORT = 5672

RABBITMQ_USER = os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_DEFAULT_PASS')


EXCHANGE_FANOUT = 'exchange_anuncios'
EXCHANGE_DIRECT = 'exchange_tareas'
EXCHANGE_TOPIC = 'exchange_proyectos'

QUEUE_ANUNCIOS = 'cola_anuncios'
QUEUE_TAREAS = 'cola_tareas'
QUEUE_PROYECTOS = 'cola_proyectos'
