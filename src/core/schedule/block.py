# src/core/schedule/schedule_block.py


from src.model.schedule.service import (
    ScheduleBlock,
)


class ScheduleBlockService:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.schedule_block = ScheduleBlock

    def add_block_schedule(self, data: dict): ...

    def list_block_schedule(self, data: dict): ...

    def delete_block_schedule(self, id: int): ...
