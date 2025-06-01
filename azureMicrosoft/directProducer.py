from azure.servicebus import ServiceBusClient, ServiceBusMessage
from config import settings
import json

def sendAzureTask(messageBodyJsonString):
    if not settings.AZURE_SERVICE_BUS_SENDER_CONNECTION_STRING or not settings.AZURE_QUEUE_NAME:
        print("[Azure] No se puede enviar tarea: Faltan credenciales de Azure Service Bus o nombre de cola.")
        return

    serviceBusClient = None # Definir fuera del try para que esté disponible en finally
    try:
        serviceBusClient = ServiceBusClient.from_connection_string(
            conn_str=settings.AZURE_SERVICE_BUS_SENDER_CONNECTION_STRING,
            logging_enable=False
        )
        sender = serviceBusClient.get_queue_sender(queue_name=settings.AZURE_QUEUE_NAME)

        with sender:
            messageToSend = ServiceBusMessage(messageBodyJsonString)
            sender.send_messages(messageToSend)
            try:
                data = json.loads(messageBodyJsonString)
                targetUser = data.get("targetUser", "desconocido") # Asumimos que el payload tiene targetUser
                print(f"[Azure] Tarea enviada a Azure Service Bus para {targetUser}: {messageBodyJsonString}")
            except json.JSONDecodeError:
                print(f"[Azure] Tarea enviada a Azure Service Bus (payload no JSON): {messageBodyJsonString}")
    except Exception as e:
        print(f"[Azure] Error enviando tarea a Azure Service Bus: {e}")
    finally:
        if serviceBusClient: # Verificar si se inicializó antes de intentar cerrar
            serviceBusClient.close()