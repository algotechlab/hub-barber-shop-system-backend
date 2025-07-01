# src/core/schedule.py

import traceback
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import jsonify
from sqlalchemy import func, insert, or_, select, update
from src.bot.schedule import Scheduler
from src.db.database import db
from src.model.model import (
    BlockScheduleService,
    BoxAccounting,
    Employee,
    Invoice,
    Products,
    ScheduleService,
    User,
)
from src.service.redis import SessionManager
from src.utils.log import logdb
from src.utils.metadata import Metadata

SCHEDULE_FIELDS = [
    "product_id",
    "employee_id",
    "time_register",
]


class ScheduleCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.schedule = ScheduleService
        self.product = Products
        self.employee = Employee
        self.user = User
        self.invoice = Invoice
        self.box_accounting = BoxAccounting
        self.block_schedule_service = BlockScheduleService
        self.session = SessionManager()

    def __parser_iso_format(self, dt_str: str) -> datetime:
        if dt_str.endswith("Z"):
            dt_str = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str)

    def dispach_summary_client(self, product_id: int, employee_id: int, schedule_data: str):
        try:
            datetime_obj = self.__parser_iso_format(schedule_data)
            stmt_product = select(self.product.description).where(
                self.product.id == product_id, self.product.is_deleted.is_(False)
            )
            product_name = db.session.execute(stmt_product).scalar_one_or_none() or "Serviço"
            stmt_employee = select(self.employee.username).where(
                self.employee.id == employee_id, self.employee.is_deleted.is_(False)
            )
            employee_name = db.session.execute(stmt_employee).scalar_one_or_none() or "Barbeiro"
            return {
                "product_name": product_name,
                "employee_name": employee_name,
                "datetime": datetime_obj.astimezone(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M")
            }
        except Exception as e:
            logdb(
                "error",
                message=f"Error dispach summary client: {e}{traceback.format_exc()}",
            )
            return None

    def add_schedule(self, data: dict):
        try:
            time_register_str = self.__parser_iso_format(
                dt_str=data.get("time_register")
            )
            user_id = data.get("user_id")
            product_id = data.get("product_id")
            employee_id = data.get("employee_id")

            # Validar entrada
            if not all([user_id, product_id, employee_id, time_register_str]):
                return (
                    jsonify({
                        "status_code": 400,
                        "message_id": "missing_parameters",
                        "error": True,
                        "message": "Missing required parameters: user_id, product_id, employee_id, or time_register"
                    }),
                    400,
                )

            # Verificar se o usuário existe e obter o número de telefone
            stmt_user = select(self.user.phone).where(
                self.user.id == user_id, self.user.is_deleted.is_(False)
            )
            client_number = db.session.execute(stmt_user).scalar_one_or_none()
            if not client_number:
                return (
                    jsonify({
                        "status_code": 404,
                        "message_id": "user_not_found",
                        "error": True,
                        "message": f"User with ID {user_id} not found"
                    }),
                    404,
                )

            # Inserir o agendamento no banco
            stmt = insert(self.schedule).values(
                product_id=product_id,
                employee_id=employee_id,
                time_register=time_register_str,
                user_id=user_id,
                is_awayalone=False,
                is_check=False,
            )
            result = db.session.execute(stmt)
            db.session.commit()
            schedule_id = result.inserted_primary_key[0]

            # Obter informações para as mensagens
            summary = self.dispach_summary_client(product_id, employee_id, data.get("time_register"))
            if not summary:
                db.session.rollback()
                return (
                    jsonify({
                        "status_code": 500,
                        "message_id": "failed_to_generate_summary",
                        "error": True,
                        "message": "Failed to generate schedule summary"
                    }),
                    500,
                )

            # Instanciar o Scheduler para enviar mensagens
            scheduler = Scheduler(message="", sender_number=client_number)

            # Salvar estado pendente no Redis
            self.session.set(
                f"pending_schedule:{employee_id}",
                json.dumps({
                    "schedule_id": schedule_id,
                    "client_number": client_number,
                    "datetime": time_register_str.isoformat(),
                    "product_id": product_id,
                    "user_id": user_id
                }),
                expire_seconds=3600  # Expira em 1 hora
            )

            # Enviar mensagem ao barbeiro
            success = scheduler.send_message_employee(
                employee_id=employee_id,
                user_id=user_id,
                product_id=product_id,
                datetime_obj=time_register_str,
            )
            if not success:
                db.session.rollback()
                return (
                    jsonify({
                        "status_code": 500,
                        "message_id": "failed_to_notify_employee",
                        "error": True,
                        "message": "Failed to notify employee"
                    }),
                    500,
                )

            # send message to client
            message = (
                f"✅ Agendamento registrado para {summary['datetime']}"
                f"com barbeiro {summary['employee_name']} para o serviço {summary['product_name']}!\n\n"
                f"Aguardando o barbeiro {summary['employee_name']} confirmar o agendamento.\n\n"
                "Digite 'menu' para voltar ao início."
            )
            scheduler._send_client_message(client_number=client_number, message=message)

            return (
                jsonify({
                    "status_code": 200,
                    "message_id": "success_add_schedule",
                    "error": False,
                    "message": "Schedule added successfully",
                    "data": summary
                }),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error add schedule: {e}{traceback.format_exc()}",
            )
            return (
                jsonify({
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                    "error": True,
                    "message": "Failed to add schedule"
                }),
                500,
            )

    def list_schedule(self, data: dict):
        try:
            stmt = (
                select(
                    self.schedule.id,
                    self.employee.id.label("employee_id"),
                    self.user.id.label("user_id"),
                    self.employee.username.label("name_employee"),
                    self.product.id.label("product_id"),
                    self.product.description.label("description"),
                    self.schedule.time_register.label("time_register"),
                    func.to_char(
                        self.product.time_to_spend, "HH24:MI:SS"
                    ).label("time_to_spend"),
                    self.user.username.label("name_client"),
                    self.user.phone.label("phone"),
                    (
                        self.schedule.time_register
                        + self.product.time_to_spend
                    ).label("end_time"),
                )
                .join(
                    self.employee,
                    self.schedule.employee_id == self.employee.id,
                )
                .join(
                    self.product, self.schedule.product_id == self.product.id
                )
                .join(self.user, self.user.id == self.schedule.user_id)
                .where(~self.schedule.is_deleted)
                .where(~self.schedule.is_check)
                .where(~self.product.is_deleted)
            )

            filter_by = data.get("filter_by")
            if filter_by:
                filter_value = f"%{filter_by}%"
                stmt = stmt.filter(
                    or_(
                        func.unaccent(self.employee.username).ilike(
                            func.unaccent(filter_value)
                        ),
                        func.unaccent(self.user.username).ilike(
                            func.unaccent(filter_value)
                        ),
                    )
                )

            result_raw = db.session.execute(stmt).fetchall()

            if not result_raw:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "schedule_not_found",
                            "error": False,
                        }
                    ),
                    404,
                )

            converted_result = []
            for row in result_raw:
                row_dict = dict(row._mapping)
                time_register = row_dict.get("time_register")
                end_time = row_dict.get("end_time")

                # Formatar time_register
                if time_register and isinstance(time_register, datetime):
                    if time_register.tzinfo is None:
                        time_register = time_register.replace(
                            tzinfo=ZoneInfo("UTC")
                        )
                    row_dict["time_register"] = time_register.astimezone(
                        ZoneInfo("America/Sao_Paulo")
                    ).strftime("%d-%m-%Y %H:%M:%S")

                # Formatar end_time
                if end_time and isinstance(end_time, datetime):
                    if end_time.tzinfo is None:
                        end_time = end_time.replace(tzinfo=ZoneInfo("UTC"))
                    row_dict["end_time"] = end_time.astimezone(
                        ZoneInfo("America/Sao_Paulo")
                    ).strftime("%d-%m-%Y %H:%M:%S")

                converted_result.append(row_dict)

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_list_schedule",
                        "error": False,
                        "data": converted_result,
                    }
                ),
                200,
            )

        except Exception as e:
            logdb(
                "error",
                message=f"Error in list_schedule: \
                {str(e)}\n{traceback.format_exc()}",
            )
            db.session.rollback()
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "internal_server_error",
                        "error": str(e),
                    }
                ),
                500,
            )

    def get_schedule(self):
        try:
            stmt = (
                select(
                    self.schedule.id,
                    self.employee.id.label("employee_id"),
                    self.user.id.label("user_id"),
                    self.employee.username.label("name_employee"),
                    self.product.description.label("description"),
                    self.schedule.time_register.label("time_register"),
                    func.to_char(
                        self.product.time_to_spend, "HH24:MI:SS"
                    ).label("time_to_spend"),
                    self.user.username.label("name_client"),
                    self.user.phone.label("phone"),
                    (
                        self.schedule.time_register
                        + self.product.time_to_spend
                    ).label("end_time"),
                )
                .join(
                    self.employee,
                    self.employee.id == self.schedule.employee_id,
                )
                .join(
                    self.product, self.schedule.product_id == self.product.id
                )
                .join(self.user, self.schedule.user_id == self.user.id)
                .where(self.schedule.is_deleted == False)
                .where(self.schedule.is_check == False)
                .where(self.schedule.user_id == int(self.user_id))
            )
            result_raw = db.session.execute(stmt).fetchall()

            if not result_raw:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "schedule_not_found",
                            "error": False,
                        }
                    ),
                    404,
                )
            converted_result = []
            for row in result_raw:
                row_dict = dict(row._mapping)
                time_register = row_dict.get("time_register")
                end_time = row_dict.get("end_time")

                # Formatar time_register
                if time_register and isinstance(time_register, datetime):
                    if time_register.tzinfo is None:
                        time_register = time_register.replace(
                            tzinfo=ZoneInfo("UTC")
                        )
                    row_dict["time_register"] = time_register.astimezone(
                        ZoneInfo("America/Sao_Paulo")
                    ).strftime("%d-%m-%Y %H:%M:%S")

                # Formatar end_time
                if end_time and isinstance(end_time, datetime):
                    if end_time.tzinfo is None:
                        end_time = end_time.replace(tzinfo=ZoneInfo("UTC"))
                    row_dict["end_time"] = end_time.astimezone(
                        ZoneInfo("America/Sao_Paulo")
                    ).strftime("%d-%m-%Y %H:%M:%S")

                converted_result.append(row_dict)

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_list_schedule",
                        "error": False,
                        "data": converted_result,
                    }
                ),
                200,
            )

        except Exception as e:
            logdb(
                "error",
                message=f"Error in get_schedule: \
                {str(e)}\n{traceback.format_exc()}",
            )
            db.session.rollback()
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "internal_server_error",
                        "error": str(e),
                    }
                ),
                500,
            )

    def check_schedule(self, id: int, data: dict):
        try:
            schedule_check = (
                update(self.schedule)
                .where(self.schedule.id == id)
                .values(is_check=True)
                .returning(self.schedule.id)
            )

            schedule_result = db.session.execute(schedule_check)
            schedule_id = schedule_result.scalar()

            check_tip = data.get("tip", 0)
            check_value_operation = data.get("value_operation", 0)

            invoice_stmt = (
                insert(self.invoice)
                .values(
                    product_id=data.get("product_id"),
                    payments_id=data.get("payment_id"),
                    schedule_id=schedule_id,
                    user_id=data.get("user_id"),
                )
                .returning(self.invoice.id)
            )

            invoice_result = db.session.execute(invoice_stmt)
            invoice_id = invoice_result.scalar()
            db.session.commit()

            box_accounting = insert(self.box_accounting).values(
                value_operation=check_value_operation,
                invoice_id=invoice_id,
                tip=check_tip,
            )
            db.session.execute(box_accounting)
            db.session.commit()

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_check_schedule",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            logdb(
                "error",
                message=f"Error in check_schedule: \
                {str(e)}\n{traceback.format_exc()}",
            )
            db.session.rollback()
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "internal_server_error",
                        "error": str(e),
                    }
                ),
                500,
            )

    def update_schedule(self, id: int, data: dict):
        try:
            if not id:
                return (
                    jsonify(
                        {
                            "status_code": 400,
                            "message_id": "id_is_required",
                        }
                    ),
                    400,
                )

            self.schedule = db.session.get(ScheduleService, id)
            if not self.schedule:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "schedule_not_found",
                        }
                    ),
                    404,
                )

            for key, value in data.items():
                if value is not None and key in SCHEDULE_FIELDS:
                    setattr(self.schedule, key, value)

            self.schedule.updated_by = self.user_id
            self.schedule.updated_at = datetime.now()

            db.session.commit()

            return {
                "status_code": 200,
                "message_id": "success_update_schedule",
                "error": False,
            }, 200

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error update schedule: \
                {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )

    def delete_schedule(self, id: int):
        try:
            stmt = (
                update(self.schedule)
                .where(~self.schedule.is_deleted, self.schedule.id == id)
                .values(
                    deleted_by=self.user_id,
                    deleted_at=datetime.now(),
                    is_deleted=True,
                )
            )

            db.session.execute(stmt)
            db.session.commit()

            return (
                jsonify(
                    (
                        {
                            "status_code": 200,
                            "message_id": "success_delete_schedule",
                            "error": False,
                        }
                    )
                )
            ), 200

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error delete schedule: \
                {e}{traceback.format_exc()}",
            )
            return (
                jsonify(
                    (
                        {
                            "status_code": 500,
                            "message_id": "something_went_wrong",
                            "traceback": traceback.format_exc(),
                        },
                    )
                ),
                500,
            )()

    def add_block_schedule(self, data: dict):
        try:
            stmt = insert(self.block_schedule_service).values(
                time_register=data.get("time_register"),
                employee_id=data.get("employee_id"),
                time_block=data.get("duration"),
                is_block=True,
            )
            db.session.execute(stmt)
            db.session.commit()
            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_block_schedule",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error block schedule: \
                {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )

    def list_block_schedule(self):
        try:
            stmt = (
                select(
                    self.block_schedule_service.id,
                    self.block_schedule_service.employee_id,
                    func.to_char(
                        self.block_schedule_service.time_register,
                        "YYYY-MM-DD HH:MM:SS",
                    ).label("time_register"),
                    func.to_char(
                        self.block_schedule_service.time_block, "HH:MM"
                    ).label("duration"),
                )
                .where(
                    self.block_schedule_service.is_block == True,
                    self.block_schedule_service.is_deleted == False,
                )
                .order_by(self.block_schedule_service.id)
            )

            result = db.session.execute(stmt).fetchall()

            if not result:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "schedule_not_found",
                            "error": True,
                        }
                    ),
                    404,
                )

            return jsonify(
                {
                    "status_code": 200,
                    "data": Metadata(result).model_to_list(),
                    "message_id": "list_block_schedule_success",
                    "error": False,
                }
            )
        except Exception as e:
            logdb(
                "error",
                message=f"Error list block schedule: \
                {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )

    def delete_block_schedule(self, id: int):
        try:
            stmt = (
                update(self.block_schedule_service)
                .where(
                    ~self.block_schedule_service.is_deleted,
                    self.block_schedule_service.id == id,
                )
                .values(
                    deleted_by=self.user_id,
                    deleted_at=datetime.now(),
                    is_deleted=True,
                    is_block=False,
                )
            )

            db.session.execute(stmt)
            db.session.commit()

            return jsonify(
                {
                    "status_code": 200,
                    "message_id": "delete_block_schedule_success",
                }
            )

        except Exception as e:
            print("Error coletado", e)
            logdb(
                "error",
                message=f"Error list block schedule: \
                {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )
