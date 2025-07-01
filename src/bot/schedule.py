# src/bot/schedule.py

import requests
import os
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import delete, insert, select, update

from src.bot.helpers.schedule_helpers import HelpersScheduler
from src.bot.response_dictionary import RESPONSE_DICTIONARY, TIME_SLOTS_CONFIG
from src.db.database import db
from src.model.model import Employee, Products, ScheduleService, User
from src.service.redis import SessionManager


URL_INSTANCE_EVOLUTION = os.getenv(
    "URL_INSTANCE_EVOLUTION",
    "http://localhost:8080/message/sendText/chatbot_barber",
)
# EVOLUTION_APIKEY = os.getenv("EVOLUTION_AP")

EVOLUTION_APIKEY = "CAF4D3F98976-485B-BC05-8880DDE44F94"


class Scheduler(HelpersScheduler):
    def __init__(self, message: str, sender_number: str, *args, **kwargs):
        super().__init__(sender_number, *args, **kwargs)
        self.message = message.strip().lower()
        self.sender_number = sender_number
        self.session = SessionManager()

    def handle_schedule(self):
        state = self.session.get(self.sender_number)
        print(f"DEBUG: Estado atual para {self.sender_number}: {state}")

        if self.message == "menu":
            print(
                f"DEBUG: User requested menu, resetting state for {self.sender_number}"
            )
            return self._reset_session()

        if not self.identify_user():
            self.session.set(self.sender_number, "undefined")
            print(
                f"DEBUG: User not identified, set state to undefined for {self.sender_number}"
            )
            return (
                "Você precisa se cadastrar primeiro. Envie seu nome completo.\n\n"
                "Digite 'menu' para voltar ao início."
            )

        if state == "undefined":
            try:
                employees = self.get_employees()
                if not employees:
                    return self._reset_session(
                        {
                            "error": "Não há barbeiros disponíveis no momento.\n\n"
                            + RESPONSE_DICTIONARY["default"]
                        }
                    )
                self.session.set(self.sender_number, "awaiting_employee")
                return (
                    f"⚠️ *Para escolher um barbeiro, digite o ID do barbeiro.*\n\n"
                    f"💇‍♂️💇‍♂️ *Escolha um barbeiro disponível:*"
                    f"\n{employees}\n\n"
                    "Digite 'menu' para voltar ao início."
                )
            except Exception as e:
                return self._reset_session()

        elif state == "awaiting_employee":
            try:
                if self.message == "voltar":
                    self.session.set(self.sender_number, "undefined")
                    print(
                        f"DEBUG: Returning to undefined state for {self.sender_number}"
                    )
                    return self.handle_schedule()

                if not self.message.isdigit():
                    print(
                        f"WARNING: Invalid employee ID input: {self.message}"
                    )
                    return (
                        "Por favor, digite o ID do barbeiro.\n\n"
                        "Digite 'voltar' para retornar ou 'menu' para voltar ao início."
                    )

                employee_id = int(self.message)
                if not self.validate_employee(employee_id):
                    print(
                        f"WARNING: Invalid employee ID {employee_id} for {self.sender_number}"
                    )
                    return (
                        "ID de barbeiro inválido. Escolha um ID da lista.\n\n"
                        "Digite 'voltar' para retornar ou 'menu' para voltar ao início."
                    )

                self.session.set(
                    self.sender_number, f"awaiting_product:{employee_id}"
                )
                self.session.set(
                    f"{self.sender_number}_employee_id", str(employee_id)
                )
                print(
                    f"DEBUG: Set state to awaiting_product:{employee_id} for {self.sender_number}"
                )
                products = self.get_products()
                if not products:
                    print("WARNING: No products available")
                    return (
                        "Nenhum serviço disponível no momento.\n\n"
                        "Digite 'menu' para voltar ao início."
                    )
                return (
                    f"Escolha um serviço:\n{products}\n\n"
                    "Digite 'voltar' para escolher outro barbeiro ou 'menu' para voltar ao início."
                )
            except Exception as e:
                print(f"ERROR: Error handling employee selection: {e}")
                return self._reset_session()

        elif state.startswith("awaiting_product"):
            try:
                if self.message == "voltar":
                    self.session.set(self.sender_number, "awaiting_employee")
                    print(
                        f"DEBUG: Returning to awaiting_employee for {self.sender_number}"
                    )
                    return self.handle_schedule()

                if not self.message.isdigit():
                    print(f"WARNING: Invalid product ID input: {self.message}")
                    return (
                        "Por favor, digite o ID do serviço.\n\n"
                        "Digite 'voltar' para escolher outro barbeiro ou 'menu' para voltar ao início."
                    )

                employee_id = state.split(":")[1]
                product_id = int(self.message)

                is_valid_product = self.validate_product(product_id)
                print(
                    f"DEBUG: Validating product ID {product_id}: {is_valid_product}"
                )
                if not is_valid_product:
                    print(
                        f"WARNING: Invalid product ID {product_id} for {self.sender_number}"
                    )
                    return (
                        "ID de serviço inválido. Escolha um ID da lista.\n\n"
                        "Digite 'voltar' para escolher outro barbeiro ou 'menu' para voltar ao início."
                    )

                self.session.set(
                    self.sender_number,
                    f"awaiting_period:{employee_id}:{product_id}",
                )
                self.session.set(
                    f"{self.sender_number}_scheduler_state",
                    f"awaiting_period:{employee_id}:{product_id}",
                )
                print(
                    f"DEBUG: Set state to awaiting_period:{employee_id}:{product_id} for {self.sender_number}"
                )
                return RESPONSE_DICTIONARY["period_selection"]
            except Exception as e:
                print(f"ERROR: Error handling product selection: {e}")
                return (
                    "Erro ao processar o serviço. Tente novamente.\n\n"
                    "Digite 'voltar' para escolher outro barbeiro ou 'menu' para voltar ao início."
                )

        elif state.startswith("awaiting_slot"):
            try:
                if self.message == "voltar":
                    _, employee_id, product_id, _ = state.split(":")
                    self.session.set(
                        self.sender_number,
                        f"awaiting_period:{employee_id}:{product_id}",
                    )
                    self.session.set(
                        f"{self.sender_number}_scheduler_state",
                        f"awaiting_period:{employee_id}:{product_id}",
                    )
                    print(
                        f"DEBUG: Returning to awaiting_period:{employee_id}:{product_id} for {self.sender_number}"
                    )
                    return RESPONSE_DICTIONARY["period_selection"]

                options = json.loads(
                    self.session.get(f"{self.sender_number}_slots") or "[]"
                )
                if not self.message.isdigit() or int(
                    self.message
                ) not in range(1, len(options) + 1):
                    print(f"WARNING: Invalid slot selection: {self.message}")
                    return (
                        "Seleção inválida. Escolha um número da lista.\n\n"
                        "Digite 'voltar' para retornar ou 'menu' para voltar ao início."
                    )

                _, employee_id, product_id, time_period = state.split(":")
                user_id = self.identify_user()
                if not user_id:
                    self.session.set(self.sender_number, "undefined")
                    print(
                        f"ERROR: User not found, set state to undefined for {self.sender_number}"
                    )
                    return (
                        "Erro: usuário não encontrado. Por favor, cadastre-se novamente.\n\n"
                        "Digite 'menu' para voltar ao início."
                    )

                selected_time_str = options[int(self.message) - 1]
                today = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
                time_obj = datetime.strptime(selected_time_str, "%H:%M").time()
                datetime_obj = datetime.combine(today, time_obj).astimezone(
                    ZoneInfo("UTC")
                )

                result = self.register_schedule(
                    user_id, product_id, employee_id, datetime_obj
                )
                print(
                    f"INFO: Agendamento registrado para {self.sender_number} às {selected_time_str}"
                )
                return result
            except Exception as e:
                print(f"ERROR: Error handling slot selection: {e}")
                return (
                    "Erro ao selecionar o horário. Tente novamente.\n\n"
                    "Digite 'voltar' para retornar ou 'menu' para voltar ao início."
                )

        print(f"WARNING: Unhandled state {state} for {self.sender_number}")
        return self._reset_session()

    def _get_available_slots(self, period: str, employee_id: int) -> list:
        """Obtém horários disponíveis para um período e funcionário específico."""
        config = TIME_SLOTS_CONFIG.get(period)
        if not config:
            print(f"ERROR: Invalid period in get_available_slots: {period}")
            return []

        occupied_slots = self._get_occupied_slots(period, employee_id)
        available_slots = [
            slot for slot in config["slots"] if slot not in occupied_slots
        ]
        print(
            f"DEBUG: Slots disponíveis para {period}, funcionário {employee_id}: {available_slots}"
        )
        return available_slots

    def _get_occupied_slots(self, period: str, employee_id: int) -> list:
        """Obtém horários ocupados para um período e funcionário específico."""
        try:
            config = TIME_SLOTS_CONFIG.get(period)
            if not config:
                print(f"ERROR: Invalid period in get_occupied_slots: {period}")
                return []

            start_time = datetime.strptime(
                config["period"].split(" - ")[0], "%H:%M"
            ).time()
            end_time = datetime.strptime(
                config["period"].split(" - ")[1], "%H:%M"
            ).time()
            today = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
            start_datetime = datetime.combine(
                today, start_time, tzinfo=ZoneInfo("America/Sao_Paulo")
            ).astimezone(ZoneInfo("UTC"))
            end_datetime = datetime.combine(
                today, end_time, tzinfo=ZoneInfo("America/Sao_Paulo")
            ).astimezone(ZoneInfo("UTC"))

            print(
                f"DEBUG: Querying schedules for employee_id={employee_id}, period={period}, start={start_datetime}, end={end_datetime}"
            )

            stmt = (
                db.session.query(
                    ScheduleService.time_register, Products.time_to_spend
                )
                .join(Products, ScheduleService.product_id == Products.id)
                .filter(
                    ScheduleService.employee_id == employee_id,
                    ScheduleService.is_deleted.is_(False),
                    ScheduleService.is_check.is_(False),
                    ScheduleService.time_register >= start_datetime,
                    ScheduleService.time_register <= end_datetime,
                )
            )
            results = db.session.execute(stmt).all()
            print(
                f"DEBUG: Found {len(results)} schedules for employee_id={employee_id} in period {period}"
            )

            occupied_slots = set()
            slot_interval = timedelta(minutes=20)

            for time_register, time_to_spend in results:
                start = time_register.astimezone(ZoneInfo("America/Sao_Paulo"))
                minutes = (
                    int(time_to_spend.total_seconds() / 60)
                    if time_to_spend
                    else 30
                )
                duration = timedelta(minutes=minutes)
                end = start + duration
                print(
                    f"DEBUG: Schedule found: start={start}, duration={minutes} minutes, end={end}"
                )

                current = start
                while current < end:
                    slot_str = current.strftime("%H:%M")
                    if slot_str in config["slots"]:
                        occupied_slots.add(slot_str)
                    current += slot_interval

            print(
                f"DEBUG: Slots ocupados para {period}, funcionário {employee_id}: {list(occupied_slots)}"
            )
            return list(occupied_slots)
        except Exception as e:
            print(f"ERROR: Erro ao obter slots ocupados: {e}")
            return []

    def _reset_session(self, message: dict = None) -> str:
        try:
            keys_to_clear = [
                f"session:{self.sender_number}",
                f"{self.sender_number}_selected_period",
                f"{self.sender_number}_slots",
                f"{self.sender_number}_scheduler_state",
                f"{self.sender_number}_employee_id",
            ]
            for key in keys_to_clear:
                self.session.delete(key)
                print(f"DEBUG: Cleared Redis key {key}")
            print(f"INFO: Session reset for {self.sender_number}")
            return (
                message.get("error", RESPONSE_DICTIONARY["default"])
                if message
                else RESPONSE_DICTIONARY["default"]
            )
        except Exception as e:
            print(
                f"ERROR: Failed to reset session for {self.sender_number}: {e}"
            )
            return RESPONSE_DICTIONARY["default"]

    def list_schedules(self):
        """Lista os agendamentos ativos do usuário."""
        try:
            user_id = self.identify_user()
            if not user_id:
                self.session.set(self.sender_number, "undefined")
                print(
                    f"ERROR: User not found, set state to undefined for {self.sender_number}"
                )
                return (
                    "Erro: usuário não encontrado. Por favor, cadastre-se novamente.\n\n"
                    "Digite 'menu' para voltar ao início."
                )

            stmt = (
                db.session.query(
                    ScheduleService.id,
                    ScheduleService.time_register,
                    Employee.username,
                    Products.description,
                )
                .join(Employee, ScheduleService.employee_id == Employee.id)
                .join(Products, ScheduleService.product_id == Products.id)
                .filter(
                    ScheduleService.user_id == user_id,
                    ScheduleService.is_deleted.is_(False),
                    ScheduleService.is_check.is_(False),
                )
                .order_by(ScheduleService.time_register.desc())  # Ordena do mais recente para o mais antigo
                .limit(1)  # Pega apenas o último registro
            )
            
            schedules = db.session.execute(stmt).fetchall()
            
            if not schedules:
                print(
                    f"INFO: No active schedules found for user {self.sender_number}"
                )
                return (
                    "Você não tem agendamentos ativos no momento.\n\n"
                    + RESPONSE_DICTIONARY["default"]
                )

            # Como agora só tem 1 registro, podemos acessá-lo diretamente
            s = schedules[0]
            agendamento_str = (
                f"Registro do agendamento: {s.id}: *{s.time_register.astimezone(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M')}*" 
                f"\n\n💇‍♂️ {s.username}"
                f"\n\n✂️ *{s.description}*"
            )
            
            print(
                f"DEBUG: Last schedule for {self.sender_number}: {agendamento_str}"
            )
            
            return RESPONSE_DICTIONARY["meus_agendamentos"].format(
                agendamentos=agendamento_str
            )
        except Exception as e:
            print(
                f"ERROR: Failed to list schedules for {self.sender_number}: {e}"
            )
            return (
                "Erro ao listar agendamentos. Tente novamente.\n\n"
                + RESPONSE_DICTIONARY["default"]
            )

    def cancel_schedule(self):
        try:
            if self.message == "menu":
                print(
                    f"DEBUG: User requested menu, resetting state for {self.sender_number}"
                )
                return self._reset_session()

            user_id = self.identify_user()
            if not user_id:
                self.session.set(self.sender_number, "undefined")
                print(
                    f"ERROR: User not found, set state to undefined for {self.sender_number}"
                )
                return (
                    "Erro: usuário não encontrado. Por favor, cadastre-se novamente.\n\n"
                    "Digite 'menu' para voltar ao início."
                )

            if self.session.get(self.sender_number) != "awaiting_cancel_id":
                stmt = (
                    db.session.query(
                        ScheduleService.id,
                        ScheduleService.time_register,
                        Employee.username,
                        Products.description,
                    )
                    .join(Employee, ScheduleService.employee_id == Employee.id)
                    .join(Products, ScheduleService.product_id == Products.id)
                    .filter(
                        ScheduleService.user_id == user_id,
                        ScheduleService.is_deleted.is_(False),
                        ScheduleService.is_check.is_(False),
                    )
                    .order_by(ScheduleService.time_register)
                )
                schedules = db.session.execute(stmt).all()
                if not schedules:
                    print(
                        f"INFO: No active schedules found for user {self.sender_number}"
                    )
                    return (
                        "💤🗓️Você não tem agendamentos *ativos* para cancelar.\n\n"
                        + RESPONSE_DICTIONARY["default"]
                    )

                agendamentos = [
                    f"*ID {s.id}*: {s.time_register.astimezone(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M')}"
                    f"com *{s.username}* para *{s.description}*"
                    for s in schedules
                ]
                agendamentos_str = "\n".join(agendamentos)
                self.session.set(self.sender_number, "awaiting_cancel_id")
                print(
                    f"DEBUG: Set state to awaiting_cancel_id for {self.sender_number}"
                )
                return RESPONSE_DICTIONARY["cancelar"].format(
                    agendamentos=agendamentos_str
                )

            if not self.message.isdigit():
                print(
                    f"WARNING: Invalid cancellation ID input: {self.message}"
                )
                return (
                    "Por favor, informe um ID numérico válido do agendamento.\n\n"
                    "Digite 'menu' para voltar ao início."
                )

            schedule_id = int(self.message)
            stmt = db.session.query(ScheduleService).filter(
                ScheduleService.id == schedule_id,
                ScheduleService.user_id == user_id,
                ScheduleService.is_deleted.is_(False),
                ScheduleService.is_check.is_(True),
            )
            schedule = db.session.execute(stmt).scalar_one_or_none()
            if not schedule:
                print(
                    f"WARNING: Agendamento não encontrado para ID {schedule_id}"
                )
                return (
                    "🗓️👥 *Agendamento não encontrado ou já cancelado.*\n\n"
                    + RESPONSE_DICTIONARY["default"]
                )
                
            stmt = delete(ScheduleService).where(
                ScheduleService.id == schedule_id
            )
            db.session.execute(stmt)
            db.session.commit()
            print(
                f"INFO: Agendamento ID {schedule_id} cancelado com sucesso para {self.sender_number}"
            )
            return self._reset_session(
                {
                    "success": (
                        f"✅ Agendamento ID {schedule_id} cancelado com sucesso.\n\n"
                        + RESPONSE_DICTIONARY["default"]
                    )
                }
            )
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Failed to cancel schedule: {e}")
            return self._reset_session(
                {
                    "error": (
                        "Erro ao cancelar agendamento. Tente novamente.\n\n"
                        + RESPONSE_DICTIONARY["default"]
                    )
                }
            )

    def validate_product(self, product_id: int) -> bool:
        """Valida se o product_id existe e não está deletado."""
        try:
            stmt = select(Products.id).where(
                Products.id == product_id, Products.is_deleted.is_(False)
            )
            result = db.session.execute(stmt).scalar_one_or_none()
            is_valid = result is not None
            print(f"DEBUG: Product validation for ID {product_id}: {is_valid}")
            return is_valid
        except Exception as e:
            print(f"ERROR: Failed to validate product {product_id}: {e}")
            return False

    # TODO ANALISAR ISSO COM OS FATOS
    def process_employee_response(self, employee_id: int, response: str) -> str:
        try:
            pending_data = self.session.get(f"pending_schedule:{employee_id}")
            if not pending_data:
                print(f"ERROR: No pending schedule found for employee {employee_id}")
                return "Nenhum agendamento pendente para confirmar."

            schedule_data = json.loads(pending_data)
            schedule_id = schedule_data["schedule_id"]
            client_number = schedule_data["client_number"]
            datetime_obj = datetime.fromisoformat(schedule_data["datetime"])
            product_id = schedule_data["product_id"]
            user_id = schedule_data["user_id"]

            if response.lower() == "confirmar":
                stmt = (
                    update(ScheduleService)
                    .where(ScheduleService.id == schedule_id)
                    .values(is_check=True)
                )
                db.session.execute(stmt)
                db.session.commit()
                self.session.delete(f"pending_schedule:{employee_id}")
                print(f"INFO: Schedule {schedule_id} confirmed by employee {employee_id}")

                # Buscar informações para a mensagem ao cliente
                stmt_product = select(Products.description).where(
                    Products.id == product_id, Products.is_deleted.is_(False)
                )
                product_name = db.session.execute(stmt_product).scalar_one_or_none() or "Serviço"
                stmt_employee = select(Employee.username).where(
                    Employee.id == employee_id, Employee.is_deleted.is_(False)
                )
                employee_name = db.session.execute(stmt_employee).scalar_one_or_none() or "Barbeiro"

                client_message = (
                    f"✅ Seu agendamento foi confirmado pelo barbeiro *{employee_name}* "
                    f"para {datetime_obj.astimezone(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M')}"
                    f"({product_name})!\n\n"
                    + RESPONSE_DICTIONARY["default"]
                )
                self._send_client_message(client_number=client_number, client_message=client_message)
                return "Agendamento confirmado com sucesso!"

            elif response.lower() == "recusar":
                stmt = delete(ScheduleService).where(ScheduleService.id == schedule_id)
                db.session.execute(stmt)
                db.session.commit()
                self.session.delete(f"pending_schedule:{employee_id}")
                print(f"INFO: Schedule {schedule_id} rejected by employee {employee_id}")

                # Buscar informações para a mensagem ao cliente
                stmt_product = select(Products.description).where(
                    Products.id == product_id, Products.is_deleted.is_(False)
                )
                product_name = db.session.execute(stmt_product).scalar_one_or_none() or "Serviço"
                stmt_employee = select(Employee.username).where(
                    Employee.id == employee_id, Employee.is_deleted.is_(False)
                )
                employee_name = db.session.execute(stmt_employee).scalar_one_or_none() or "Barbeiro"

                client_message = (
                    f"❌ Seu agendamento para {datetime_obj.astimezone(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M')} "
                    f"({product_name}) com *{employee_name}* foi recusado pelo barbeiro. "
                    f"Por favor, escolha outro horário.\n\n"
                    + RESPONSE_DICTIONARY["default"]
                )
                self._send_client_message(client_number=client_number, client_message=client_message)
                return "Agendamento recusado."

            else:
                return "Por favor, responda com 'Confirmar' ou 'Recusar'."
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Failed to process employee response: {e}")
            return "Erro ao processar sua resposta. Tente novamente."

    def _send_client_message(self, client_number: str, message: str):
        try:
            payload = {
                "number": client_number,
                "text": message,
                "delay": 2000,
            }
            headers = {
                "apikey": EVOLUTION_APIKEY,
                "Content-Type": "application/json",
            }
            response = requests.post(
                url=URL_INSTANCE_EVOLUTION,
                json=payload,
                headers=headers,
                timeout=5
            )
            if response.status_code == 201:
                print(f"INFO: Message sent to client {client_number}")
            else:
                print(f"ERROR: Failed to send message to client {client_number}: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"ERROR: Failed to send message to client {client_number}: {e}")

    def send_message_employee(self, employee_id: int, user_id: int, product_id: int, datetime_obj: datetime) -> bool:
        try:
            # Buscar o telefone do barbeiro
            print("PROOCESSANDO A FUNÇÃO QUE PROCESSAR O EMPLOYEE")
            stmt = select(Employee.phone, Employee.username).where(
                Employee.id == employee_id, Employee.is_deleted.is_(False)
            )
            result = db.session.execute(stmt).first()
            if not result:
                print(f"ERROR: Employee with ID {employee_id} not found or deleted")
                return False
            employee_phone, employee_name = result

            # Buscar informações do cliente
            stmt_user = select(User.username).where(User.id == user_id)
            user_name = db.session.execute(stmt_user).scalar_one_or_none() or "Cliente"

            # Buscar informações do serviço
            stmt_product = select(Products.description).where(
                Products.id == product_id, Products.is_deleted.is_(False)
            )
            product_name = db.session.execute(stmt_product).scalar_one_or_none() or "Serviço"

            # Formatando a mensagem para o barbeiro
            formatted_time = datetime_obj.astimezone(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M")
            message = (
                f"📅 *Novo Agendamento*\n"
                f"Cliente: {user_name}\n"
                f"Serviço: {product_name}\n"
                f"Horário: {formatted_time}\n"
                f"Por favor, confirme se você pode atender este agendamento respondendo 'Confirmar' ou 'Recusar'."
            )

            # Enviando a mensagem via Evolution API
            payload = {
                "number": employee_phone,
                "text": message,
                "delay": 2000,
            }
            headers = {
                "apikey": EVOLUTION_APIKEY,
                "Content-Type": "application/json",
            }
            response = requests.post(
                url=URL_INSTANCE_EVOLUTION,
                json=payload,
                headers=headers,
                timeout=5
            )

            if response.status_code == 201:
                print(f"INFO: Message sent to employee {employee_name} ({employee_phone}) for schedule at {formatted_time}")
                return True
            else:
                print(
                    f"ERROR: Failed to send message to employee {employee_id}: {response.status_code}, {response.text}"
                )
                return False

        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Failed to send message to employee {employee_id}: {e}")
            return False

    def register_schedule(
        self,
        user_id: int,
        product_id: int,
        employee_id: int,
        datetime_obj: datetime,
    ):
        try:
            # Verificar conflitos
            stmt = (
                db.session.query(ScheduleService)
                .join(Products, ScheduleService.product_id == Products.id)
                .filter(
                    ScheduleService.employee_id == employee_id,
                    ScheduleService.is_deleted.is_(False),
                    ScheduleService.is_check.is_(False),
                    ScheduleService.time_register <= datetime_obj,
                    (ScheduleService.time_register + Products.time_to_spend)
                    > datetime_obj,
                )
            )
            conflict = db.session.execute(stmt).first()
            if conflict:
                print(
                    f"ERROR: Scheduling conflict for employee_id={employee_id} at {datetime_obj}"
                )
                return (
                    "Erro: horário já ocupado. Escolha outro horário.\n\n"
                    + RESPONSE_DICTIONARY["default"]
                )

            # Inserir agendamento
            print(
                f"DEBUG: Attempting to insert schedule: user_id={user_id}, product_id={product_id}, employee_id={employee_id}, time={datetime_obj}"
            )
            stmt = insert(ScheduleService).values(
                product_id=int(product_id),
                employee_id=int(employee_id),
                user_id=user_id,
                time_register=datetime_obj,
                is_awayalone=False,
                is_check=False,
            )
            result = db.session.execute(stmt)
            db.session.commit()
            schedule_id = result.inserted_primary_key[0]
            print(
                f"INFO: Schedule inserted successfully for user_id {user_id}, product_id={product_id}, employee_id={employee_id}, time={datetime_obj}, schedule_id={schedule_id}"
            )

            try:
                stmt_employee = select(Employee.username).where(
                    Employee.id == employee_id, Employee.is_deleted.is_(False)
                )
                employee_name = (
                    db.session.execute(stmt_employee).scalar_one_or_none()
                    or "Barbeiro"
                )
            except Exception as e:
                print(
                    f"ERROR: Failed to fetch employee name for ID {employee_id}: {e}"
                )
                employee_name = "Barbeiro"

            try:
                stmt_product = select(Products.description).where(
                    Products.id == product_id, Products.is_deleted.is_(False)
                )
                product_name = (
                    db.session.execute(stmt_product).scalar_one_or_none()
                    or "Serviço"
                )
            except Exception as e:
                print(
                    f"ERROR: Failed to fetch product name for ID {product_id}: {e}"
                )
                product_name = "Serviço"

            self._reset_session()
            print(
                f"INFO: Session reset for {self.sender_number} after scheduling"
            )

            # send message employee
            self.send_message_employee(
                employee_id=employee_id,
                user_id=user_id,
                product_id=product_id,
                datetime_obj=datetime_obj,
            )
            return (
                f"✅ Agendamento confirmado para {datetime_obj.astimezone(ZoneInfo('America/Sao_Paulo')).strftime('%H:%M')} "
                f"com *{employee_name}* para o serviço *{product_name}*!\n\n"
                f"Aguardando o barbeiro *{employee_name}* confirmar o agendamento.\n\n"
                + RESPONSE_DICTIONARY["default"]
            )
        except Exception as e:
            print(
                f"ERROR: Failed to insert schedule for {self.sender_number}: {e}"
            )
            db.session.rollback()
            return (
                "Erro ao realizar agendamento. Tente novamente.\n\n"
                + RESPONSE_DICTIONARY["default"]
            )
