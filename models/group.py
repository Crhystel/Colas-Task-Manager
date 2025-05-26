class Group:
    def __init__(self, name):
        self.name = name
        self.members = []

    def add_user(self, user):
        self.members.append(user)

    def __str__(self):
        return f"Grupo: {self.name}, Miembros: {[u.username for u in self.members]}"
