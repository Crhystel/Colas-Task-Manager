import json
import os
from messageService import MessageService # Gestiona los procesos de los consumidores
from rabbitmq.fanoutProducer import sendAnnouncement # Envía anuncios generales (RabbitMQ)
from rabbitmq.topicProducer import sendProyect # Envía proyectos por tema (RabbitMQ)
from messageProducer import sendTaskToQueues # Envía tareas directas (Azure)

USERS_FILE = "users.json" # Archivo para almacenar datos de usuarios

# Carga los usuarios registrados desde el archivo JSON
def loadUser():
    if not os.path.exists(USERS_FILE):
        return [] # Retorna lista vacía si el archivo no existe
    with open(USERS_FILE, "r") as f:
        return json.load(f)

# Guarda la lista de usuarios en el archivo JSON
def saveUser(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4) # indent=4 para formato legible

# Valida las credenciales del usuario para iniciar sesión
def login():
    usuarios = loadUser()
    print("=== Login ===")
    username = input("Usuario: ").strip()
    password = input("Contraseña: ").strip()

    for user in usuarios:
        if user["username"] == username and user["password"] == password:
            print(f"\nBienvenido {user['username']}! Rol: {user['role']}, Grupo: {user['group']}\n")
            return user # Retorna el diccionario del usuario si las credenciales son correctas
    print("Credenciales incorrectas.\n")
    return None # Retorna None si el login falla

# Permite crear un nuevo usuario y guardarlo
def createUser():
    print("=== Crear nuevo usuario ===")
    username = input("Nuevo usuario: ").strip()
    password = input("Contraseña: ").strip()
    role = input("Rol (admin/profesor/estudiante): ").strip().lower()
    group = input("Grupo (grupo1/grupo2/...): ").strip().lower()

    users = loadUser()
    # Verifica si el usuario ya existe
    if any(u["username"] == username for u in users):
        print("El usuario ya existe.\n")
        return

    users.append({
        "username": username,
        "password": password,
        "role": role,
        "group": group
    })
    saveUser(users)
    print("Usuario creado correctamente.\n")

# Muestra la lista de todos los usuarios registrados
def seeUsers():
    users = loadUser()
    print("=== Lista de usuarios ===")
    for user in users:
        print(f" {user['username']} | Rol: {user['role']} | Grupo: {user['group']}")
    print()

# Menú principal de la aplicación, varía según el rol del usuario
def menu(currentUser): 
    msgService = MessageService() # Instancia el servicio de mensajería
    msgService.startForUser(currentUser["username"], currentUser["role"], currentUser["group"]) # Inicia consumidores

    while True:
        # Menú para administradores
        if currentUser["role"] == "admin":
            print("1. Crear usuario")
            print("2. Ver todos los usuarios")
            print("3. Enviar anuncio general ")
            print("4. Asignar tarea a usuario")
            print("5. Publicar proyecto por grupo/rol")
            print("0. Cerrar sesión")
            option = input("Seleccione opción: ") 

            match option:
                case "1":
                    createUser()
                case "2":
                    seeUsers()
                case "3": # Enviar anuncio general
                    msg = input("Mensaje anuncio general: ")
                    sendAnnouncement(msg) 
                    print("Anuncio enviado.\n")
                case "4": # Asignar tarea directa
                    destUserName = input("Usuario destinatario: ") 
                    taskTitle = input("Título de la tarea: ")  
                    taskContent = input("Mensaje de la tarea: ")
                    sendTaskToQueues(destUserName, taskTitle, taskContent) # Envía a Azure
                    print("Solicitud de envío de tarea procesada.\n")
                case "5": # Publicar proyecto por tema
                    routingKey = input("Routing key (rol.grupo): ")
                    projectMessage = input("Mensaje proyecto: ") 
                    sendProyect(routingKey, projectMessage) 
                    print("Proyecto enviado.\n")
                case "0": # Cerrar sesión
                    print("Cerrando sesión...\n")
                    msgService.stopAll() # Detiene todos los consumidores
                    return
                case _:
                    print("Opción inválida.\n")

        # Menú para estudiantes
        elif currentUser["role"] == "estudiante":
            # (El bucle while True interno para el estudiante es redundante si el menú se reimprime)
            # Lo mantendré como estaba en tu código original, pero podría simplificarse.
            while True:
                print("1. Ver mis tareas asignadas")
                print("2. Enviar mensaje a otro usuario ")
                print("0. Cerrar sesión")
                option = input("Seleccione opción: ")

                match option:
                    case "1": # Ver tareas desde archivo
                        taskFilePath = f"tasks/{currentUser['username']}.txt" 
                        if os.path.exists(taskFilePath):
                            print(f"\n=== Tareas de {currentUser['username']} ===")
                            with open(taskFilePath, "r", encoding="utf-8") as f:
                                content = f.read()
                                print(content if content else "No tienes tareas registradas.\n")
                        else:
                            print("\nNo tienes tareas registradas.\n")

                    case "2": # Enviar mensaje directo (tarea) a otro usuario
                        recipientUserName = input("Usuario destinatario: ").strip() 
                        messageContent = input("Mensaje que deseas enviar: ").strip() 
                        messageTitle = f"Mensaje de {currentUser['username']}" 
                        sendTaskToQueues(recipientUserName, messageTitle, messageContent) # Envía a Azure
                        print("Solicitud de envío de mensaje procesada.\n")

                    case "0": # Cerrar sesión
                        print("Cerrando sesión...\n")
                        msgService.stopAll()
                        return
                    case _:
                        print("Opción inválida.\n")
        
        # Menú para profesores
        elif currentUser["role"] == "profesor":
            print("1. Asignar tarea a estudiante")
            print("0. Cerrar sesión")
            option = input("Seleccione una opción: ")

            match option:
                case "1": # Asignar tarea a un estudiante
                    destUserName = input("Estudiante destinatario: ") 
                    taskTitle = input("Título de la tarea: ") 
                    taskContent = input("Descripción de la tarea: ") 
                    sendTaskToQueues(destUserName, taskTitle, taskContent) # Envía a Azure
                    print("Solicitud de asignación de tarea procesada.\n")
                case "0": # Cerrar sesión
                    print("Cerrando sesión...\n")
                    msgService.stopAll()
                    return
                case _:
                    print("Opción inválida.\n")

# Función principal que maneja el flujo de login y menú
def main():
    while True:
        currentUser = None
        # Bucle hasta que el login sea exitoso
        while not currentUser:
            currentUser = login()
        menu(currentUser) # Pasa al menú del usuario logueado

if __name__ == "__main__":
    main() # Punto de entrada de la aplicación