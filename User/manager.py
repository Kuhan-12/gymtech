from flask_login import UserMixin

class User(UserMixin):
    def __init__(self,id,Username,Password):
        self.id = id
        self.Username = Username
        self.Password = Password
    def get_id(self):
        return (self.id)
    