def login(users):
    username = input("Usuario: ")
    password = input("Contraseña: ")

    for user in users:
        if user.username == username and user.password == password:
            print(f"Bienvenido {user.username} ({user.role})")
            return user
    print("Credenciales incorrectas.")
    return None
