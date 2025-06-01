import json
import os
from messageService import MessageService# Asumiendo que está en la raíz o en PYTHONPATH
from rabbitmq.fanoutProducer import sendAnnouncement # Se mantiene para RabbitMQ
# from rabbitmq.directProducer import sendTarea # Ya no se usa directamente aquí, se usa el unificado
from rabbitmq.topicProducer import sendProyect # Se mantiene para RabbitMQ
from messageProducer import sendTaskToQueues # Nuevo productor unificado

# El resto de tus importaciones y funciones (cargarUsuarios, guardarUsuarios, login, crearUsuario, verUsuarios) se mantienen igual.
# ... (tu código de cargarUsuarios, guardarUsuarios, login, crearUsuario, verUsuarios) ...

USERS_FILE = "users.json"

# Carga los usuarios registrados desde el archivo
def loadUser():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

# Guarda los usuarios en el archivo
def saveUser(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Inicia sesión si las credenciales coinciden
def login():
    usuarios = loadUser()
    print("=== Login ===")
    username = input("Usuario: ").strip()
    password = input("Contraseña: ").strip()

    for user in usuarios:
        if user["username"] == username and user["password"] == password:
            print(f"\nBienvenido {user['username']}! Rol: {user['role']}, Grupo: {user['group']}\n")
            return user
    print("Credenciales incorrectas.\n")
    return None

# Crea un nuevo usuario (solo admins)
def createUser():
    print("=== Crear nuevo usuario ===")
    username = input("Nuevo usuario: ").strip()
    password = input("Contraseña: ").strip()
    role = input("Rol (admin/profesor/estudiante): ").strip().lower()
    group = input("Grupo (grupo1/grupo2/...): ").strip().lower()

    users = loadUser()
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

# Muestra todos los usuarios
def seeUsers():
    users = loadUser()
    print("=== Lista de usuarios ===")
    for user in users:
        print(f" {user['username']} | Rol: {user['role']} | Grupo: {user['group']}")
    print()


def menu(currentUser): # Cambiado a camelCase
    msgService = MessageService()
    # En MessageService, userName, userRole, userGroup ya son camelCase
    msgService.startForUser(currentUser["username"], currentUser["role"], currentUser["group"])

    while True:
        if currentUser["role"] == "admin":
            print("1. Crear usuario")
            print("2. Ver todos los usuarios")
            print("3. Enviar anuncio general")
            print("4. Asignar tarea a usuario")
            print("5. Publicar proyecto por grupo/rol")
            print("0. Cerrar sesión")
            option = input("Seleccione opción: ") # Cambiado a camelCase

            match option:
                case "1":
                    createUser()
                case "2":
                    seeUsers()
                case "3":
                    msg = input("Mensaje anuncio general: ")
                    sendAnnouncement(msg) # Esto sigue siendo solo RabbitMQ
                    print("Anuncio enviado.\n")
                case "4":
                    destUserName = input("Usuario destinatario: ") # Cambiado a camelCase
                    taskTitle = input("Título de la tarea: ")    # Cambiado a camelCase
                    taskContent = input("Mensaje de la tarea: ") # Cambiado a camelCase
                    
                    # Usar el nuevo productor unificado
                    sendTaskToQueues(destUserName, taskTitle, taskContent)
                    print("Solicitud de envío de tarea procesada.\n")
                case "5":
                    routingKey = input("Routing key (rol.grupo): ")
                    projectMessage = input("Mensaje proyecto: ") # Cambiado a camelCase
                    sendProyect(routingKey, projectMessage) # Esto sigue siendo solo RabbitMQ
                    print("Proyecto enviado.\n")
                case "0":
                    print("Cerrando sesión...\n")
                    msgService.stopAll()
                    return
                case _:
                    print("Opción inválida.\n")

        elif currentUser["role"] == "estudiante":
            # ... (resto del menú de estudiante, actualizando las llamadas de envío de tareas) ...
            while True:
                print("1. Ver mis tareas asignadas")
                print("2. Enviar mensaje a otro usuario")
                print("0. Cerrar sesión")
                option = input("Seleccione opción: ")

                match option:
                    case "1":
                        # La lógica de lectura de tareas se mantiene, leerá de los archivos
                        # que ahora pueden ser poblados por RabbitMQ o Azure
                        taskFilePath = f"tasks/{currentUser['username']}.txt" # Cambiado a camelCase
                        if os.path.exists(taskFilePath):
                            print(f"\n=== Tareas de {currentUser['username']} ===")
                            with open(taskFilePath, "r", encoding="utf-8") as f:
                                content = f.read()
                                print(content if content else "No tienes tareas registradas.\n")
                        else:
                            print("\nNo tienes tareas registradas.\n")

                    case "2":
                        recipientUserName = input("Usuario destinatario: ").strip() # Cambiado a camelCase
                        messageContent = input("Mensaje que deseas enviar: ").strip() # Cambiado a camelCase
                        messageTitle = f"Mensaje de {currentUser['username']}" # Cambiado a camelCase
                        
                        # Usar el nuevo productor unificado
                        sendTaskToQueues(recipientUserName, messageTitle, messageContent)
                        print("Solicitud de envío de mensaje procesada.\n")

                    case "0":
                        print("Cerrando sesión...\n")
                        msgService.stopAll()
                        return

                    case _:
                        print("Opción inválida.\n")
        
        elif currentUser["role"] == "profesor":
            # ... (resto del menú de profesor, actualizando las llamadas de envío de tareas) ...
            print("1. Asignar tarea a estudiante")
            print("0. Cerrar sesión")
            option = input("Seleccione una opción: ")

            match option:
                case "1":
                    destUserName = input("Estudiante destinatario: ") # Cambiado a camelCase
                    taskTitle = input("Título de la tarea: ") # Cambiado a camelCase
                    taskContent = input("Descripción de la tarea: ") # Cambiado a camelCase
                    
                    # Usar el nuevo productor unificado
                    sendTaskToQueues(destUserName, taskTitle, taskContent)
                    print("Solicitud de asignación de tarea procesada.\n")
                case "0":
                    print("Cerrando sesión...\n")
                    msgService.stopAll()
                    return
                case _:
                    print("Opción inválida.\n")

# Punto de entrada de la app
def main():
    while True:
        currentUser = None # Cambiado a camelCase
        while not currentUser:
            currentUser = login()
        menu(currentUser)

if __name__ == "__main__":
    main()