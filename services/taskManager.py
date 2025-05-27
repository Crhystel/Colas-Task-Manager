from models.task import Task

class TaskManager:
    def __init__(self):
        self.tasks = []

    def crearTarea(self, title, description, assigned_to):
        task = Task(title, description, assigned_to)
        self.tasks.append(task)
        print(f"Tarea '{title}' creada para {assigned_to}")
        return task

    def obtenerTareasPorUsuario(self, username):
        return [t for t in self.tasks if t.assigned_to == username]

    def obtenerTodasTareas(self):
        return self.tasks

    def eliminarTarea(self, title):
        self.tasks = [t for t in self.tasks if t.title != title]
        print(f"Tarea '{title}' eliminada.")

    def reasignarTarea(self, title, nuevo_usuario):
        for task in self.tasks:
            if task.title == title:
                task.assigned_to = nuevo_usuario
                print(f"Tarea '{title}' reasignada a {nuevo_usuario}")
                return True
        print(f"No se encontró la tarea '{title}'")
        return False
