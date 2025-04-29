# src/core/user.py
from werkzeug.security import generate_password_hash

from src.model.model import User


class UserCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.user = User
    
    def get_user(self, id: int):
        ...
    
    def add_user(self, data: dict):
        ...
        
    def list_users(self, data: dict):
        ...
    
    def update_user(self, id: int, data: dict):
        ...
        
    def delete(self, id: int):
        ...