from azure.servicebus import ServiceBusClient
from config import settings
import os
from datetime import datetime
import json
import time

def startAzureDirectConsumer(userNameForFile):
    """Inicia un consumidor para mensajes directos de Azure Service Bus."""

    if not settings.AZURE_SERVICE_BUS_RECEIVER_CONNECTION_STRING or not settings.AZURE_QUEUE_NAME:
        print(f"[Azure Consumer - {userNameForFile}] Configuración de Azure incompleta.")
        return

    # Configuración de directorios para logs y tareas
    projectRootDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    logsDir = os.path.join(projectRootDir, "logs")
    taskDir = os.path.join(projectRootDir, "tasks")
    os.makedirs(logsDir, exist_ok=True)
    os.makedirs(taskDir, exist_ok=True)
    logFilePath = os.path.join(logsDir, f"direct_{userNameForFile}.log")
    taskFilePath = os.path.join(taskDir, f"{userNameForFile}.txt")

    serviceBusClient = None
    try:
        # Conexión a Azure Service Bus
        serviceBusClient = ServiceBusClient.from_connection_string(
            conn_str=settings.AZURE_SERVICE_BUS_RECEIVER_CONNECTION_STRING,
            logging_enable=False
        )
        receiver = serviceBusClient.get_queue_receiver(queue_name=settings.AZURE_QUEUE_NAME)
        print(f"[Azure Consumer - {userNameForFile}] Esperando tareas en '{settings.AZURE_QUEUE_NAME}'...")

        with receiver: # Bucle principal de recepción de mensajes
            while True:
                receivedMessages = receiver.receive_messages(max_wait_time=10)
                for msg in receivedMessages:
                    try:
                        data = json.loads(str(msg)) # Parsea el mensaje JSON
                        targetUser = data.get("targetUser")

                        if targetUser == userNameForFile: # Procesa si el mensaje es para este usuario
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print(f"\n[Azure Direct] {userNameForFile} recibió tarea vía Azure.\n")
                            with open(taskFilePath, "a", encoding="utf-8") as f_task:
                                f_task.write(f"[{timestamp}] Tarea (Azure): {data.get('titulo', 'Sin título')} - {data.get('contenido', 'Sin contenido')}\n")
                            with open(logFilePath, "a", encoding="utf-8") as f_log:
                                f_log.write(f"[{timestamp}] Tarea recibida (Azure): {str(msg)}\n")
                            receiver.complete_message(msg) # Confirma y elimina el mensaje
                        
                        elif targetUser: # Mensaje para otro usuario, ignorar
                            print(f"[Azure Consumer - {userNameForFile}] Mensaje para '{targetUser}' ignorado.")
                        
                        else: # Mensaje sin 'targetUser', completar para evitar reprocesamiento
                            print(f"[Azure Consumer - {userNameForFile}] Mensaje sin 'targetUser': {str(msg)}")
                            receiver.complete_message(msg)
                    
                    except Exception as e: # Manejo de errores durante el procesamiento del mensaje
                        error_message = f"[{datetime.now()}] Error procesando mensaje Azure: {e} - Raw: {str(msg)}\n"
                        print(f"[Azure Consumer - {userNameForFile}] {error_message.strip()}")
                        with open(logFilePath, "a", encoding="utf-8") as f_log_err:
                            f_log_err.write(error_message)
                        receiver.complete_message(msg) # Completar para evitar bucles con mensajes erróneos
    
    except Exception as e: # Error crítico del consumidor
        print(f"[Azure Consumer - {userNameForFile}] Error crítico: {e}")
        time.sleep(10)
    finally: # Asegura el cierre del cliente
        if serviceBusClient:
            serviceBusClient.close()
        print(f"[Azure Consumer - {userNameForFile}] Consumidor de Azure detenido.")