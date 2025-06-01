import multiprocessing
from azureMicrosoft.directConsumer import startAzureDirectConsumer # Consumidor Azure para tareas directas
from rabbitmq.topicConsumer import startTopicConsumer   # Consumidor RabbitMQ para temas
from rabbitmq.fanoutConsumer import startFanoutConsumer # Consumidor RabbitMQ para anuncios
from config import settings

class MessageService:
    def __init__(self):
        self.processes = [] # Almacena los procesos de los consumidores

    def startForUser(self, userName, userRole, userGroup):
        """Inicia los consumidores para un usuario."""
        print(f"[+] Iniciando consumidores para {userName} ({userRole}.{userGroup})\n")

        # Consumidor Azure para tareas directas
        if settings.AZURE_SERVICE_BUS_RECEIVER_CONNECTION_STRING and settings.AZURE_QUEUE_NAME:
            pDirectAzure = multiprocessing.Process(target=startAzureDirectConsumer, args=(userName,))
            pDirectAzure.start()
            self.processes.append(pDirectAzure)
            print(f"[+] Iniciado consumidor de Azure para tareas directas de {userName}")
        else:
            print(f"[-] No se iniciará el consumidor de Azure para {userName} por configuración faltante.")

        # Consumidor RabbitMQ para temas (proyectos)
        topicKey = f"{userRole}.{userGroup}"
        pTopicRabbit = multiprocessing.Process(target=startTopicConsumer, args=(topicKey,))
        pTopicRabbit.start()
        self.processes.append(pTopicRabbit)
        print(f"[+] Iniciado consumidor de RabbitMQ por tema ({topicKey}) para {userName}")

        # Consumidor RabbitMQ para fanout (anuncios)
        pFanoutRabbit = multiprocessing.Process(target=startFanoutConsumer)
        pFanoutRabbit.start()
        self.processes.append(pFanoutRabbit)
        print(f"[+] Iniciado consumidor de RabbitMQ fanout (anuncios) para {userName}")

    def stopAll(self):
        """Detiene todos los procesos de consumidores."""
        print("[x] Deteniendo consumidores...")
        for p in self.processes:
            if p.is_alive():
                p.terminate()
                p.join(timeout=5) 
                if p.is_alive(): 
                    p.kill() 
                    p.join()
        self.processes.clear()
        print("[x] Todos los consumidores detenidos.")