from azure.servicebus import ServiceBusClient, ServiceBusMessage
import os

CONNECTION_STR = os.getenv("AZURE_SERVICE_BUS_SENDER")
QUEUE_NAME = "Tareas"

def sendTarea(usuario, mensaje):
    full_message = f"{usuario}:{mensaje}"
    with ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR) as client:
        sender = client.get_queue_sender(queue_name=QUEUE_NAME)
        with sender:
            msg = ServiceBusMessage(full_message)
            sender.send_messages(msg)
            print(f"[AzureSB] Tarea enviada a {usuario}")
