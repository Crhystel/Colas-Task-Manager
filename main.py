from models.user import User
from models.group import Group
from models.role import Role
from models.task import Task
from services.authorization import login

# Datos simulados
users = []
groups = []
tasks = []

# Crear primer admin por defecto
admin_user = User("admin","123admin",Role.ADMIN,"ADMIN GROUP")
users.append(admin_user)

def crear_usuario():
    username = input("Nombre de usuario: ")
    password = input("Contraseña: ")
    print("Roles disponibles:", ", ".join(Role.list_roles()))
    role = input("Rol: ")
    group_name = input("Grupo: ")

    group = next((g for g in groups if g.name == group_name), None)
    if not group:
        group = Group(group_name)
        groups.append(group)

    user = User(username, password, role, group.name)
    users.append(user)
    group.add_user(user)
    print("Usuario creado con éxito.")

def crear_tarea(logged_user):
    title = input("Título de la tarea: ")
    description = input("Descripción: ")

    if logged_user.role == Role.ADMIN:
        assigned_to = input("Asignar a (username): ")
    else:
        assigned_to = logged_user.username

    if any(u.username == assigned_to for u in users):
        task = Task(title, description, assigned_to)
        tasks.append(task)
        print("Tarea creada y asignada.")
    else:
        print("Usuario no encontrado.")

def ver_tareas(logged_user):
    if logged_user.role == Role.ADMIN:
        for task in tasks:
            print(task)
    else:
        for task in tasks:
            if task.assigned_to == logged_user.username:
                print(task)

def ver_usuarios():
    for user in users:
        print(user)

def menu_admin():
    while True:
        print("\n--- Menú ADMIN ---")
        print("1. Crear usuario")
        print("2. Crear tarea")
        print("3. Ver tareas")
        print("4. Ver usuarios")
        print("5. Salir")

        opcion = input("Opción: ")
        if opcion == "1":
            crear_usuario()
        elif opcion == "2":
            crear_tarea(logged_user=admin_user)
        elif opcion == "3":
            ver_tareas(logged_user=admin_user)
        elif opcion == "4":
            ver_usuarios()
        elif opcion == "5":
            break
        else:
            print("Opción inválida.")

def menu_usuario(logged_user):
    while True:
        print(f"\n--- Menú ({logged_user.role}) ---")
        print("1. Crear tarea")
        print("2. Ver mis tareas")
        print("3. Salir")

        opcion = input("Opción: ")
        if opcion == "1":
            crear_tarea(logged_user)
        elif opcion == "2":
            ver_tareas(logged_user)
        elif opcion == "3":
            break
        else:
            print("Opción inválida.")

def menu_principal():
    while True:
        print("\n=== LOGIN ===")
        user = login(users)
        if user:
            if user.role == Role.ADMIN:
                menu_admin()
            else:
                menu_usuario(user)

if __name__ == "__main__":
    menu_principal()
