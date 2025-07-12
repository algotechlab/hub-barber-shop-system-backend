# src/model/model.py
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Interval, Numeric, func
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import db


class Log(db.Model):
    __tablename__ = "logs"
    __table_args__ = {"schema": "audit_logs"}

    id: Mapped[int] = mapped_column(
        db.Integer, primary_key=True, autoincrement=True
    )
    timestamp: Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    logger_name: Mapped[str] = mapped_column(db.Text, nullable=False)
    level: Mapped[str] = mapped_column(db.Text, nullable=False)
    message: Mapped[str] = mapped_column(db.Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, server_default=func.now(), nullable=True
    )

    def __repr__(self):
        return (
            f"<Log: Loggin registred at {self.timestamp} - "
            f"{self.logger_name} - {self.level} - {self.message}>"
        )


class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(120), nullable=False)
    lastname: Mapped[str] = mapped_column(db.String(120), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(40), nullable=False)
    session_token: Mapped[str] = mapped_column(db.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"""{self.username} created successfully"""


class Employee(db.Model):
    __tablename__ = "employee"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(120), nullable=False)
    date_of_birth: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False
    )
    phone: Mapped[str] = mapped_column(db.String(40), nullable=False)
    role: Mapped[str] = mapped_column(db.String(40), nullable=False)
    session_token: Mapped[str] = mapped_column(db.Text, nullable=True)
    password: Mapped[str] = mapped_column(db.String(300), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=True, server_default=func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"""{self.username} created employeesuccessfully"""


class Products(db.Model):
    __tablename__ = "products"
    __table_args__ = {"schema": "finance"}

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(db.String(30), nullable=False)
    value_operation: Mapped[Numeric] = mapped_column(
        db.Numeric(2, 10), default=0.00
    )
    time_to_spend: Mapped[Interval] = mapped_column(Interval, nullable=False)
    commission: Mapped[float] = mapped_column(db.Float, nullable=False)
    category: Mapped[str] = mapped_column(db.String(20), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"""{self.description} created successfully"""


class ProductsEmployees(db.Model):
    __tablename__ = "products_employees"
    __table_args__ = {"schema": "finance"}

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("finance.products.id"), nullable=False
    )
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("public.employee.id"), nullable=False
    )
    is_check: Mapped[bool] = mapped_column(db.Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"""{self.id} created successfully"""


class ScheduleService(db.Model):
    __tablename__ = "schedule_service"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    time_register: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    product_id: Mapped[int] = mapped_column(db.Integer, nullable=False)
    employee_id: Mapped[int] = mapped_column(db.Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(db.Integer, nullable=False)
    is_check: Mapped[int] = mapped_column(db.Boolean, nullable=False)
    is_awayalone: Mapped[int] = mapped_column(db.Boolean, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"""{self.id} created successfully"""


class Avaliable(db.Model):
    __tablename__ = "avaliable"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    star: Mapped[int] = mapped_column(db.Integer, nullable=False)
    product_id: Mapped[int] = mapped_column(db.Integer, nullable=False)
    employee_id: Mapped[int] = mapped_column(db.Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(db.Integer, nullable=False)
    observer: Mapped[str] = mapped_column(db.String(20), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"""{self.id} created successfully"""


class Subscription(db.Model):
    __tablename__ = "subscription"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(225), nullable=False)
    price: Mapped[Decimal] = mapped_column(db.Numeric(10, 2), default=0.00)
    days_to_spend: Mapped[str] = mapped_column(INTERVAL, nullable=False)
    benefits: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    users: Mapped[list["SubscriptionUser"]] = relationship(
        "SubscriptionUser", back_populates="subscription"
    )

    def __repr__(self):
        return f"<Subscription {self.name}>"


class SubscriptionUser(db.Model):
    __tablename__ = "subscription_user"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(
        ForeignKey("public.subscription.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("public.user.id"), nullable=False
    )
    start_subscription: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False
    )
    end_subscription: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    subscription: Mapped["Subscription"] = relationship(
        "Subscription",
        back_populates="users",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    def __repr__(self):
        return f"<SubscriptionUser id={self.id}, user_id={self.user_id}>"


class Payments(db.Model):
    __tablename__ = "payments"
    __table_args__ = {"schema": "finance"}

    id: Mapped[int] = mapped_column(primary_key=True)
    type_payments: Mapped[str] = mapped_column(db.String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Payments id={self.id}, type_payments={self.type_payments}>"


class Invoice(db.Model):
    __tablename__ = "invoice"
    __table_args__ = {"schema": "finance"}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("public.user.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("public.products.id"), nullable=False
    )
    payments_id: Mapped[int] = mapped_column(
        ForeignKey("finance.payments.id"), nullable=False
    )
    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("public.schedule_service.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"""<Invoice id={self.id}"""


class BoxAccounting(db.Model):
    __tablename__ = "box_accounting"
    __table_args__ = {"schema": "finance"}

    id: Mapped[int] = mapped_column(primary_key=True)
    value_operation: Mapped[float] = mapped_column(
        db.Numeric(10, 2), default=0.00
    )
    tip: Mapped[float] = mapped_column(db.Numeric(10, 2), default=0.00)
    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("finance.invoice.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"""<BoxAccounting id={self.id}"""


class BlockScheduleService(db.Model):
    __tablename__ = "block_schedule_service"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    time_register: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False
    )
    time_block: Mapped[str] = mapped_column(INTERVAL, nullable=False)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("public.employee.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)
    is_block: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"""<Created BlockScheduleService id={self.id}>"""


class InvoiceOutPut(db.Model):
    __tablename__ = "invoice_out_put"
    __table_args__ = {"schema": "finance"}

    id: Mapped[int] = mapped_column(primary_key=True)
    value_operation: Mapped[float] = mapped_column(
        db.Numeric(10, 2), default=0.00
    )
    types_payments: Mapped[str] = mapped_column(db.String(30), nullable=False)
    description: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"""<InvoiceOutPut id={self.id}>"""


class IndicatedUsers(db.Model):
    __tablename__ = "indicated_users"
    __table_args__ = {"schema": "campaign"}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("public.user.id"), nullable=False
    )
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("public.employee.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)
