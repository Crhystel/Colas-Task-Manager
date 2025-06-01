from azure.servicebus import ServiceBusClient
from azure.servicebus import ServiceBusReceiveMode
import os
import json
from datetime import datetime
import time

queueName = "tareas"

def processMessage(userName, messageString):
    try:
        messageData = json.loads(messageString)

        if messageData.get("toUser") == userName:
            timestampRaw = messageData.get('timestamp') or datetime.now().isoformat()
            timestampDisplay = datetime.fromisoformat(timestampRaw).strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n🔔 [AzureSB] New message for {userName} ({timestampDisplay}):")
            print(f"   From: {messageData.get('fromUser')}")
            print(f"   Subject: {messageData.get('title')}")
            print(f"   Type: {messageData.get('type')}")

            logDir = f"user_messages/{userName}"
            os.makedirs(logDir, exist_ok=True)

            fileTimestamp = datetime.fromisoformat(timestampRaw).strftime("%Y%m%d_%H%M%S_%f")
            messageTypePrefix = messageData.get('type', 'message')
            filePath = os.path.join(logDir, f"{messageTypePrefix}_{fileTimestamp}.json")

            with open(filePath, "w", encoding="utf-8") as f:
                json.dump(messageData, f, indent=4, ensure_ascii=False)
            print(f"   Message saved to: {filePath}\n> ", end="")
            return True
        else:
            return False

    except json.JSONDecodeError:
        print(f"[AzureSB Consumer - {userName}] Error: Received message is not valid JSON: {messageString}")
        return True
    except Exception as e:
        print(f"[AzureSB Consumer - {userName}] Error processing message: {e}")
        return False

def startAzureTaskConsumer(userName, stopEvent):
    connectionString = os.getenv("AZURE_SERVICE_BUS_RECEIVER")
    if not connectionString:
        print(f"[AzureSB Consumer - {userName}] ERROR: AZURE_SERVICE_BUS_RECEIVER is not configured.")
        return

    print(f"[AzureSB Consumer - {userName}] Starting Azure task/response consumer...")

    while not stopEvent.is_set():
        try:
            with ServiceBusClient.from_connection_string(conn_str=connectionString) as client:
                receiver = servicebus_client.get_queue_receiver(
                queue_name=taskQueue,
                receive_mode=ServiceBusReceiveMode.PEEK_LOCK )
                with receiver:
                    for receivedMessage in receiver:
                        if stopEvent.is_set():
                            if receivedMessage:
                                receiver.abandon_message(receivedMessage)
                            break

                        try:
                            messageContentString = b"".join(receivedMessage.body).decode("utf-8")
                        except Exception as e:
                            print(f"[AzureSB Consumer - {userName}] Error decoding message body: {e}")
                            receiver.abandon_message(receivedMessage)
                            continue

                        if processMessage(userName, messageContentString):
                            receiver.complete_message(receivedMessage)
                        else:
                            receiver.abandon_message(receivedMessage)

                        if stopEvent.is_set():
                            break

            if not stopEvent.is_set():
                time.sleep(0.5)

        except Exception as e:
            if not stopEvent.is_set():
                print(f"[AzureSB Consumer - {userName}] Error in loop: {e}. Retrying in 5s...")
                for _ in range(50):
                    if stopEvent.is_set():
                        break
                    time.sleep(0.1)

    print(f"[AzureSB Consumer - {userName}] Consumer stopped.")
