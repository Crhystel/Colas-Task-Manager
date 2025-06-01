from azure.servicebus import ServiceBusClient, ServiceBusMessage # SDK de Azure Service Bus
from config import settings # Archivo de configuración con las credenciales y nombres de cola
import json # Para manejar datos en formato JSON

def sendAzureTask(messageBodyJsonString):
    """Envía un mensaje (string JSON) a la cola configurada en Azure Service Bus."""

    # Verifica que las credenciales y el nombre de la cola estén presentes en la configuración
    if not settings.AZURE_SERVICE_BUS_SENDER_CONNECTION_STRING or not settings.AZURE_QUEUE_NAME:
        print("[Azure] No se puede enviar tarea: Faltan credenciales de Azure Service Bus o nombre de cola.")
        return

    serviceBusClient = None # Inicializa el cliente fuera del try para acceso en finally
    try:
        # Crea un cliente de Service Bus usando la cadena de conexión del remitente
        serviceBusClient = ServiceBusClient.from_connection_string(
            conn_str=settings.AZURE_SERVICE_BUS_SENDER_CONNECTION_STRING,
            logging_enable=False # Deshabilita el logging detallado de la SDK
        )
        # Obtiene un emisor (sender) para la cola especificada
        sender = serviceBusClient.get_queue_sender(queue_name=settings.AZURE_QUEUE_NAME)

        # Usa el emisor en un bloque 'with' para asegurar que se cierre correctamente
        with sender:
            # Crea el objeto de mensaje de Service Bus a partir del string JSON proporcionado
            messageToSend = ServiceBusMessage(messageBodyJsonString)
            # Envía el mensaje a la cola
            sender.send_messages(messageToSend)
            
            # Intenta decodificar el JSON enviado para un log más informativo (opcional)
            try:
                data = json.loads(messageBodyJsonString)
                targetUser = data.get("targetUser", "desconocido") # Extrae el usuario destino si existe
                print(f"[Azure] Tarea enviada a Azure Service Bus para {targetUser}: {messageBodyJsonString}")
            except json.JSONDecodeError:
                # Si el string no es JSON válido, solo loguea el envío del string crudo
                print(f"[Azure] Tarea enviada a Azure Service Bus (payload no JSON): {messageBodyJsonString}")
    
    except Exception as e:
        # Captura cualquier otra excepción durante el proceso de envío
        print(f"[Azure] Error enviando tarea a Azure Service Bus: {e}")
    finally:
        # Asegura que el cliente de Service Bus se cierre si fue inicializado
        if serviceBusClient: 
            serviceBusClient.close()