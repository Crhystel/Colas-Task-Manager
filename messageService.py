# messageService.py (asumiendo que este archivo está en la raíz del proyecto o en una carpeta 'services')
import multiprocessing
# La siguiente línea es la clave: el consumidor directo ahora es de Azure
from azureMicrosoft.directConsumer import startAzureDirectConsumer
from rabbitmq.topicConsumer import startTopicConsumer   # Se mantiene para RabbitMQ Topic
from rabbitmq.fanoutConsumer import startFanoutConsumer # Se mantiene para RabbitMQ Fanout
from config import settings

class MessageService:
    def __init__(self):
        self.processes = []

    def startForUser(self, userName, userRole, userGroup):
        print(f"[+] Iniciando consumidores para {userName} ({userRole}.{userGroup})\n")

        # Consumidor directo: AHORA es Azure Service Bus
        if settings.AZURE_SERVICE_BUS_RECEIVER_CONNECTION_STRING and settings.AZURE_QUEUE_NAME:
            pDirectAzure = multiprocessing.Process(target=startAzureDirectConsumer, args=(userName,))
            pDirectAzure.start()
            self.processes.append(pDirectAzure)
            print(f"[+] Iniciado consumidor de Azure para {userName}")
        else:
            print(f"[-] No se iniciará el consumidor de Azure Service Bus para {userName} debido a configuración faltante.")

        # Consumidor por tema RabbitMQ: filtra por rol.grupo (SE MANTIENE IGUAL)
        topicKey = f"{userRole}.{userGroup}"
        pTopicRabbit = multiprocessing.Process(target=startTopicConsumer, args=(topicKey,))
        pTopicRabbit.start()
        self.processes.append(pTopicRabbit)

        # Consumidor fanout RabbitMQ: escucha anuncios globales (SE MANTIENE IGUAL)
        pFanoutRabbit = multiprocessing.Process(target=startFanoutConsumer)
        pFanoutRabbit.start()
        self.processes.append(pFanoutRabbit)

    def stopAll(self):
        # ... (tu código de stopAll está bien) ...
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