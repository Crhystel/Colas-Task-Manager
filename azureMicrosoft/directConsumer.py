from azure.servicebus import ServiceBusClient
from config import settings
import os
from datetime import datetime
import json
import time

def startAzureDirectConsumer(userNameForFile):
    if not settings.AZURE_SERVICE_BUS_RECEIVER_CONNECTION_STRING or not settings.AZURE_QUEUE_NAME:
        print(f"[Azure Consumer - {userNameForFile}] No se puede iniciar: Faltan credenciales de Azure Service Bus o nombre de cola.")
        return

    baseDir = os.path.dirname(os.path.abspath(__file__))
    projectRootDir = os.path.join(baseDir, "..")
    logsDir = os.path.join(projectRootDir, "logs")
    taskDir = os.path.join(projectRootDir, "tasks")
    
    os.makedirs(logsDir, exist_ok=True)
    os.makedirs(taskDir, exist_ok=True)

    logFilePath = os.path.join(logsDir, f"direct_{userNameForFile}.log")
    taskFilePath = os.path.join(taskDir, f"{userNameForFile}.txt")

    serviceBusClient = None
    try:
        serviceBusClient = ServiceBusClient.from_connection_string(
            conn_str=settings.AZURE_SERVICE_BUS_RECEIVER_CONNECTION_STRING,
            logging_enable=False
        )
        
        receiver = serviceBusClient.get_queue_receiver(queue_name=settings.AZURE_QUEUE_NAME)
        print(f"[Azure Consumer - {userNameForFile}] Esperando tareas en la cola '{settings.AZURE_QUEUE_NAME}' de Azure Service Bus...")

        with receiver:
            while True:
                receivedMessages = receiver.receive_messages(max_wait_time=10)
                for msg in receivedMessages:
                    try:
                        msgBodyStr = str(msg)
                        data = json.loads(msgBodyStr)
                        targetUser = data.get("targetUser")

                        if targetUser == userNameForFile:
                            title = data.get("titulo", "Sin título")
                            content = data.get("contenido", "Sin contenido")
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            print(f"\n[Azure Direct] {userNameForFile} recibió tarea vía Azure.\n")

                            with open(taskFilePath, "a", encoding="utf-8") as f:
                                f.write(f"[{timestamp}] Tarea (Azure): {title} - {content}\n")
                            with open(logFilePath, "a", encoding="utf-8") as log:
                                log.write(f"[{timestamp}] Tarea recibida (Azure): {msgBodyStr}\n")
                            
                            receiver.complete_message(msg)
                        elif targetUser:
                            print(f"[Azure Consumer - {userNameForFile}] Mensaje para '{targetUser}' ignorado. Será procesado por el consumidor correcto.")
                        else:
                            print(f"[Azure Consumer - {userNameForFile}] Mensaje recibido sin 'targetUser', no se puede procesar: {msgBodyStr}")
                            receiver.complete_message(msg) # Evitar reprocesamiento
                    except json.JSONDecodeError as e:
                        print(f"[Azure Consumer - {userNameForFile}] Error decodificando JSON de Azure: {e} - Raw: {str(msg)}")
                        with open(logFilePath, "a", encoding="utf-8") as log:
                            log.write(f"[{datetime.now()}] Error Azure (JSON): {e} - Raw: {str(msg)}\n")
                        receiver.complete_message(msg)
                    except Exception as e:
                        print(f"[Azure Consumer - {userNameForFile}] Error procesando mensaje de Azure: {e}")
                        with open(logFilePath, "a", encoding="utf-8") as log:
                            log.write(f"[{datetime.now()}] Error Azure: {e} - Raw: {str(msg)}\n")
                        receiver.complete_message(msg)
    except Exception as e:
        print(f"[Azure Consumer - {userNameForFile}] Error crítico en el consumidor de Azure: {e}")
        time.sleep(10)
    finally:
        if serviceBusClient:
            serviceBusClient.close()
        print(f"[Azure Consumer - {userNameForFile}] Consumidor de Azure detenido.")