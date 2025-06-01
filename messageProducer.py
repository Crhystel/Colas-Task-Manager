import json
from azureMicrosoft.directProducer import sendAzureTask

def sendTaskToQueues(targetUserName, taskTitle, taskContent):
    """
   Sends a task message (direct) to Azure Service Bus.
    """
    # Prepare message for RabbitMQ (payload original)
    rabbitMessagePayload = {"titulo": taskTitle, "contenido": taskContent}
    rabbitMessageJson = json.dumps(rabbitMessagePayload)
    
    
    # Prepare message for Azure Service Bus (añadiendo targetUser para filtrado en el consumidor)
    azureMessagePayload = {
        "titulo": taskTitle, 
        "contenido": taskContent,
        "targetUser": targetUserName  # Crucial para que el consumidor de Azure sepa para quién es
    }
    azureMessageJson = json.dumps(azureMessagePayload)

    # Send to Azure Service Bus
    try:
        print(f"Intentando enviar tarea a Azure Service Bus para {targetUserName}...")
        sendAzureTask(azureMessageJson)
        # sendAzureTask imprime su propio mensaje de confirmación/error
    except Exception as e:
        print(f"[!] Error enviando tarea a Azure para {targetUserName}: {e}")