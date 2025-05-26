class User:
    def __init__(self,username,password,role,group):
        self.username=username
        self.password=password
        self.role=role
        self.group=group
    
    def __str__(self):
        return f"{self.username} ({self.role},{self.group})"