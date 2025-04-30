
from src.model.model import User

class LoginCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.user = User
        
        
    def login(self, data: dict):
        ...