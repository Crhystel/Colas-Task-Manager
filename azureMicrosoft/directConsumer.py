from azure.servicebus import ServiceBusClient
import os
from datetime import datetime

CONNECTION_STR = os.getenv("AZURE_SERVICE_BUS_RECEIVER")
QUEUE_NAME = "Tareas"

def startDirectConsumer(usuario):
    with ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR) as client:
        receiver = client.get_queue_receiver(queue_name=QUEUE_NAME)
        with receiver:
            for msg in receiver:
                content = str(msg)
                if content.startswith(f"{usuario}:"):
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[AzureSB] {timestamp} - Mensaje para {usuario}: {content}")
                    receiver.complete_message(msg)
