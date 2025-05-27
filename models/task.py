class Task:
    def __init__(self, title, description, assigned_to):
        self.title = title
        self.description = description
        self.assigned_to = assigned_to  
        ##

    def __str__(self):
        return f"{self.title} -> {self.assigned_to}: {self.description}"
