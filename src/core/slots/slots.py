# src/core/slots/slots.py


class Slots:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        
    def list_slots(self, employee_id: int):
        ...