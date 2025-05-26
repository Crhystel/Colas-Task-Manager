class Role:
    ADMIN="admin"
    MANAGER="manager"
    MEMBER="member"
    
    @classmethod
    def list_roles(cls):
        return[cls.ADMIN, cls.MANAGER,cls.MEMBER]