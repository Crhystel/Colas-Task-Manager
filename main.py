import json
import os
from rabbitmq.messageService import MessageService
from rabbitmq.fanoutProducer import sendAnuncio
from rabbitmq.directProducer import sendTarea
from rabbitmq.topicProducer import sendProyecto

USERS_FILE = "users.json"

def cargarUsuarios():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def guardarUsuarios(usuarios):
    with open(USERS_FILE, "w") as f:
        json.dump(usuarios, f, indent=4)

def login():
    usuarios = cargarUsuarios()
    print("=== Login ===")
    username = input("Usuario: ").strip()
    password = input("Contraseña: ").strip()

    for user in usuarios:
        if user["username"] == username and user["password"] == password:
            print(f"\nBienvenido {user['username']}! Rol: {user['role']}, Grupo: {user['group']}\n")
            return user
    print("Credenciales incorrectas.\n")
    return None

def crearUsuario():
    print("=== Crear nuevo usuario ===")
    username = input("Nuevo usuario: ").strip()
    password = input("Contraseña: ").strip()
    role = input("Rol (admin/profesor/estudiante): ").strip().lower()
    group = input("Grupo (grupo1/grupo2/...): ").strip().lower()

    usuarios = cargarUsuarios()
    if any(u["username"] == username for u in usuarios):
        print("El usuario ya existe.\n")
        return

    usuarios.append({
        "username": username,
        "password": password,
        "role": role,
        "group": group
    })
    guardarUsuarios(usuarios)
    print("Usuario creado correctamente.\n")

def verUsuarios():
    usuarios = cargarUsuarios()
    print("=== Lista de usuarios ===")
    for user in usuarios:
        print(f" {user['username']} | Rol: {user['role']} | Grupo: {user['group']}")
    print()

def menu(user):
    msgService = MessageService()
    msgService.startForUser(user["username"], user["role"], user["group"])

    while True:
        if user["role"] == "admin":
            print("1. Crear usuario")
            print("2. Ver todos los usuarios")
            print("3. Enviar anuncio general")
            print("4. Asignar tarea a usuario")
            print("5. Publicar proyecto por grupo/rol")
            print("0. Cerrar sesión")

            opcion = input("Seleccione opción: ")

            match opcion:
                case "1":
                    crearUsuario()
                case "2":
                    verUsuarios()
                case "3":
                    msg = input("Mensaje anuncio general: ")
                    sendAnuncio(msg)
                    print("Anuncio enviado.\n")
                case "4":
                    destUsuario = input("Usuario destinatario: ")
                    tarea = input("Mensaje tarea: ")
                    sendTarea(destUsuario, tarea)
                    print("Tarea enviada.\n")
                case "5":
                    routingKey = input("Routing key (rol.grupo): ")
                    proyecto = input("Mensaje proyecto: ")
                    sendProyecto(routingKey, proyecto)
                    print("Proyecto enviado.\n")
                case "0":
                    print("Cerrando sesión...\n")
                    msgService.stopAll()
                    return
                case _:
                    print("Opción inválida.\n")

        else:
            print("1. Enviar tarea a usuario")
            print("0. Cerrar sesión")

            opcion = input("Seleccione opción: ")

            match opcion:
                case "1":
                    destUsuario = input("Usuario destinatario: ")
                    tarea = input("Mensaje tarea: ")
                    sendTarea(destUsuario, tarea)
                    print("Tarea enviada.\n")
                case "0":
                    print("Cerrando sesión...\n")
                    msgService.stopAll()
                    return
                case _:
                    print("Opción inválida.\n")

def main():
    while True:
        user = None
        while not user:
            user = login()
        menu(user)

if __name__ == "__main__":
    main()
