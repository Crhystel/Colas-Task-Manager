from rabbitmq.messageService import MessageService
from rabbitmq.fanoutProducer import sendAnuncio
from rabbitmq.directProducer import sendTarea
from rabbitmq.topicProducer import sendProyecto

def login():
    print("=== Login ===")
    usuario = input("Usuario: ").strip()
    rol = input("Rol (admin/profesor/estudiante): ").strip().lower()
    grupo = input("Grupo (grupo1/grupo2/...): ").strip().lower()
    return usuario, rol, grupo

def main():
    msg_service = MessageService()

    usuario, rol, grupo = login()
    msg_service.startForUser(usuario, rol, grupo)

    print(f"\nBienvenido {usuario}! Rol: {rol}, Grupo: {grupo}\n")

    while True:
        if rol == "admin":
            print("1. Crear usuario (simulado)")
            print("2. Enviar anuncio general")
            print("3. Asignar tarea a usuario")
            print("4. Publicar proyecto por grupo/rol")
            print("0. Salir")

            opcion = input("Seleccione opción: ")

            match opcion:
                case "1":
                    print("[Simulación] Crear usuario no implementado en este ejemplo.")
                case "2":
                    msg = input("Mensaje anuncio general: ")
                    sendAnuncio(msg)
                case "3":
                    dest_usuario = input("Usuario destinatario: ")
                    tarea = input("Mensaje tarea: ")
                    sendTarea(dest_usuario, tarea)
                case "4":
                    routing_key = input("Routing key (rol.grupo): ")
                    proyecto = input("Mensaje proyecto: ")
                    sendProyecto(routing_key, proyecto)
                case "0":
                    print("Saliendo...")
                    msg_service.stopAll()
                    break
                case _:
                    print("Opción inválida.")

        else:
            print("1. Enviar tarea a usuario")
            print("0. Salir")

            opcion = input("Seleccione opción: ")

            match opcion:
                case "1":
                    dest_usuario = input("Usuario destinatario: ")
                    tarea = input("Mensaje tarea: ")
                    sendTarea(dest_usuario, tarea)
                case "0":
                    print("Saliendo...")
                    msg_service.stopAll()
                    break
                case _:
                    print("Opción inválida.")

if __name__ == "__main__":
    main()
