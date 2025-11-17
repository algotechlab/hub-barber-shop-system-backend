import math
from datetime import datetime, timedelta

from sqlalchemy import func, select

from src.db.database import db
from src.model.employee import Employee
from src.model.product import Product
from src.model.schedule import Schedule
from src.model.schedule_block import ScheduleBlock
from src.utils.metadata import ApiResponse


class SlotsService:
    def __init__(self, user_id: int, company_id: int, *args, **kwargs):
        self.db_session = db.session
        self.company_id = company_id
        self.user_id = user_id
        self.schedule = Schedule
        self.employee = Employee
        self.block = ScheduleBlock
        self.product = Product

    def ceil_to_slot(
        self, dt: datetime, anchor: datetime, slot_minutes: int
    ) -> datetime:
        """
        Arredonda dt para cima ao próximo boundary definido a partir de anchor
        Ex: anchor=09:00, slot_minutes=30 => boundaries: 09:00,09:30,10:00,...
        dt=14:10 => retorna 14:30
        """
        if dt <= anchor:
            return anchor
        seconds = (dt - anchor).total_seconds()
        slot_seconds = slot_minutes * 60
        slots = math.ceil(seconds / slot_seconds)
        return anchor + timedelta(seconds=slots * slot_seconds)

    def to_iso(self, slot):
        return {
            "start": slot["start"].isoformat(),
            "end": slot["end"].isoformat(),
        }

    def parse_datetime_or_time(
        self, value: str, default_date: datetime.date
    ) -> datetime:
        """
        Se vier ISO com data 'YYYY-MM-DDTHH:MM:SS' retorna datetime completo.
        Se vier somente 'HH:MM' ou 'HH:MM:SS' converte usando default_date.
        """
        if "T" in value:
            return datetime.fromisoformat(value)
        t = self.parse_time_iso(value)
        return datetime.combine(default_date, t)

    def list_slot(
        self, slots_data: dict, slot_minutes: int = 30
    ) -> ApiResponse:
        try:
            work_start_raw = slots_data.get("work_start")
            work_end_raw = slots_data.get("work_end")

            provided_date = None
            if slots_data.get("date"):
                provided_date = (
                    slots_data["date"]
                    if isinstance(slots_data["date"], datetime)
                    else datetime.fromisoformat(slots_data["date"]).date()
                )

            if "T" in (work_start_raw or ""):
                start_dt = datetime.fromisoformat(work_start_raw)
                end_dt = datetime.fromisoformat(work_end_raw)
                anchor = start_dt
            else:
                target_date = provided_date or datetime.now().date()
                start_dt = self.parse_datetime_or_time(
                    work_start_raw, target_date
                )
                end_dt = self.parse_datetime_or_time(work_end_raw, target_date)
                anchor = start_dt

            slots = []
            current = start_dt
            while current < end_dt:
                slots.append(
                    {
                        "start": current,
                        "end": current + timedelta(minutes=slot_minutes),
                    }
                )
                current += timedelta(minutes=slot_minutes)

            stmt = (
                select(self.schedule.time_register, self.product.time_to_spend)
                .join(
                    self.product, self.product.id == self.schedule.product_id
                )
                .where(
                    self.schedule.employee_id.__eq__(
                        slots_data.get("employee_id")
                    ),
                    self.schedule.is_deleted.__eq__(False),
                    func.date(self.schedule.time_register).__eq__(
                        anchor.date()
                    ),
                )
            )
            scheduled_rows = self.db_session.execute(stmt).all()

            scheduled_intervals = []
            for start_time, duration in scheduled_rows:
                real_end = start_time + duration
                rounded_end = self.ceil_to_slot(real_end, anchor, slot_minutes)
                scheduled_intervals.append(
                    {"start": start_time, "end": rounded_end}
                )

            block_stmt = select(
                self.block.start_time, self.block.end_time
            ).where(
                self.block.employee_id.__eq__(slots_data.get("employee_id"))
            )
            blocks_raw = self.db_session.execute(block_stmt).all()
            blocks = [{"start": b[0], "end": b[1]} for b in blocks_raw]

            def intersects(a_start, a_end, b_start, b_end):
                return a_start < b_end and a_end > b_start

            available = []
            for slot in slots:
                s0, s1 = slot["start"], slot["end"]
                # conflito com schedules?
                if any(
                    intersects(s0, s1, si["start"], si["end"])
                    for si in scheduled_intervals
                ):
                    continue
                # conflito com blocks?
                if any(
                    intersects(s0, s1, b["start"], b["end"]) for b in blocks
                ):
                    continue
                available.append(slot)

            return ApiResponse(
                status_code=200,
                data=[self.to_iso(s) for s in available],
                message="Get slots success",
                error=False,
            ).to_response()

        except Exception:
            self.db_session.rollback()
            return ApiResponse(
                error=True,
                message="Error occurred while listing slots.",
                status_code=500,
            ).to_response()
