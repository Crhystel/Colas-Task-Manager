# rabbitmq/message_service.py

import multiprocessing
from rabbitmq.directConsumer import startDirectConsumer
from rabbitmq.topicConsumer import startTopicConsumer
from rabbitmq.fanoutConsumer import startFanoutConsumer 

class MessageService:
    def __init__(self):
        self.processes = []

    def startForUser(self, username, role, group):
        print(f"[+] Iniciando consumidores para {username} ({role}.{group})")
        
        # Consumidor directo (mensajes individuales)
        p1 = multiprocessing.Process(target=startDirectConsumer, args=(username,))
        p1.start()
        self.processes.append(p1)

        # Consumidor por tema (grupo y rol)
        topic_key = f"{role}.{group}"
        p2 = multiprocessing.Process(target=startTopicConsumer, args=(topic_key,))
        p2.start()
        self.processes.append(p2)

        # Consumidor fanout (anuncios generales)
        p3 = multiprocessing.Process(target=startFanoutConsumer)
        p3.start()
        self.processes.append(p3)

    def stopAll(self):
        print("[x] Deteniendo consumidores...")
        for p in self.processes:
            p.terminate()
            p.join()
        self.processes.clear()
