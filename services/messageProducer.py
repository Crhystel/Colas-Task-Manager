import json
from azureMicrosoft.directProducer import sendAzureTask # Función para enviar mensajes a Azure

def sendTaskToQueues(targetUserName, taskTitle, taskContent):
    """Prepara y envía un mensaje de tarea a Azure Service Bus."""

    # (La sección para preparar rabbitMessagePayload no se usa si las tareas directas solo van a Azure)
    # rabbitMessagePayload = {"titulo": taskTitle, "contenido": taskContent}
    # rabbitMessageJson = json.dumps(rabbitMessagePayload)
    
    # Prepara el payload del mensaje para Azure Service Bus
    azureMessagePayload = {
        "titulo": taskTitle, 
        "contenido": taskContent,
        "targetUser": targetUserName  # Necesario para el filtrado en el consumidor de Azure
    }
    azureMessageJson = json.dumps(azureMessagePayload)

    # Intenta enviar el mensaje a Azure
    try:
        print(f"Intentando enviar tarea a Azure Service Bus para {targetUserName}...")
        sendAzureTask(azureMessageJson)
    except Exception as e:
        print(f"[!] Error enviando tarea a Azure para {targetUserName}: {e}")