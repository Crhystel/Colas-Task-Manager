from azure.servicebus import ServiceBusClient, ServiceBusMessage
import os
import json
from datetime import datetime

queueName = "tareas"

def sendAzureMessage(messageBodyJsonString):
    connectionString = os.getenv("AZURE_SERVICE_BUS_SENDER")
    if not connectionString:
        print("[AzureSB Producer] ERROR: AZURE_SERVICE_BUS_SENDER is not configured.")
        return

    try:
        with ServiceBusClient.from_connection_string(conn_str=connectionString) as client:
            sender = client.get_queue_sender(queue_name=queueName)
            with sender:
                messageToSend = ServiceBusMessage(messageBodyJsonString)
                sender.send_messages(messageToSend)
                try:
                    messageData = json.loads(messageBodyJsonString)
                    print(f"[AzureSB] Message type '{messageData.get('type', 'unknown')}' sent for '{messageData.get('toUser', 'unknown')}' via Azure.")
                except json.JSONDecodeError:
                    print(f"[AzureSB] Message sent (content not JSON for log): {messageBodyJsonString[:50]}...")
    except Exception as e:
        print(f"[AzureSB Producer] Error sending message: {e}")

def sendTaskOrResponse(fromUser, toUser, title, content, messageType="task_assignment", originalTaskId=None):
    messagePayload = {
        "fromUser": fromUser,
        "toUser": toUser,
        "title": title,
        "content": content,
        "type": messageType,
        "timestamp": datetime.now().isoformat()
    }
    if originalTaskId:
        messagePayload["originalTaskId"] = originalTaskId

    sendAzureMessage(json.dumps(messagePayload, ensure_ascii=False))
