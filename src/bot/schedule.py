# src/bot/schedule.py

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import delete

from src.bot.helpers.schedule_helpers import HelpersScheduler
from src.bot.response_dictionary import RESPONSE_DICTIONARY
from src.db.database import db
from src.model.model import ScheduleService
from src.service.redis import SessionManager
from src.utils.log import logdb


class Scheduler(HelpersScheduler):
    def __init__(self, message: str, sender_number: str, *args, **kwargs):
        self.message = message.strip().lower()
        self.sender_number = sender_number
        self.session = SessionManager()

    def handle_schedule_flow(self):
        state = self.session.get(self.sender_number)

        if self.message == "menu":
            return self.session.reset_to_default(
                self.sender_number, RESPONSE_DICTIONARY
            )

        if not self.identify_user():
            self.session.set(self.sender_number, "awaiting_register_data")
            return (
                "Você precisa se cadastrar primeiro. Envie seu nome completo.\n\n"
                "Digite 'menu' para voltar ao início."
            )

        if state == "registered":
            employees = self.get_employees()
            if not employees:
                return self.session.reset_to_default(
                    self.sender_number,
                    {
                        "error": "Não há barbeiros disponíveis no momento.\n\n"
                        + RESPONSE_DICTIONARY["default"]
                    },
                )
            self.session.set(self.sender_number, "awaiting_employee")
            return (
                f"Escolha um barbeiro:\n{employees}\n\n"
                "Digite 'menu' para voltar ao início."
            )

        elif state == "awaiting_employee":
            if self.message == "voltar":
                self.session.set(self.sender_number, "registered")
                return self.handle_schedule_flow()

            if not self.message.isdigit():
                return (
                    "Por favor, digite o ID do barbeiro.\n\n"
                    "Digite 'voltar' para retornar ou 'menu' para voltar ao início."
                )

            employee_id = int(self.message)
            if not self.validate_employee(employee_id):
                return (
                    "ID de barbeiro inválido. Escolha um ID da lista.\n\n"
                    "Digite 'voltar' para retornar ou 'menu' para voltar ao início."
                )

            self.session.set(
                self.sender_number, f"awaiting_product:{employee_id}"
            )
            products = self.get_products()
            return (
                f"Escolha um serviço:\n{products}\n\n"
                "Digite 'voltar' para escolher outro barbeiro ou 'menu' para voltar ao início."
            )

        elif state.startswith("awaiting_product"):
            if self.message == "voltar":
                self.session.set(self.sender_number, "awaiting_employee")
                return self.handle_schedule_flow()

            if not self.message.isdigit():
                return (
                    "Por favor, digite o ID do serviço.\n\n"
                    "Digite 'voltar' para escolher outro barbeiro ou 'menu' para voltar ao início."
                )

            employee_id = state.split(":")[1]
            product_id = int(self.message)

            if not self.validate_product(product_id):
                return (
                    "ID de serviço inválido. Escolha um ID da lista.\n\n"
                    "Digite 'voltar' para escolher outro barbeiro ou 'menu' para voltar ao início."
                )

            self.session.set(
                self.sender_number, f"awaiting_time:{employee_id}:{product_id}"
            )
            return (
                "Qual período prefere? manhã, tarde ou noite?\n\n"
                "Digite 'voltar' para escolher outro serviço ou 'menu' para voltar ao início."
            )

        elif state.startswith("awaiting_time"):
            if self.message == "voltar":
                employee_id = state.split(":")[1]
                self.session.set(
                    self.sender_number, f"awaiting_product:{employee_id}"
                )
                return self.handle_schedule_flow()

            time_period = self.message.strip().lower()
            if time_period not in ("manhã", "tarde", "noite"):
                return (
                    "Por favor, escolha entre manhã, tarde ou noite.\n\n"
                    "Digite 'voltar' para escolher outro serviço ou 'menu' para voltar ao início."
                )

            _, employee_id, product_id = state.split(":")
            user_id = self.identify_user()

            if not user_id:
                self.session.set(self.sender_number, "awaiting_register_data")
                return (
                    "Erro: usuário não encontrado. Por favor, cadastre-se novamente.\n\n"
                    "Digite 'menu' para voltar ao início."
                )

            all_slots = self.list_slots_employees()
            if not all_slots:
                return "Erro ao obter horários disponíveis. Tente novamente mais tarde."

            options = all_slots.get(time_period, [])
            if not options:
                return (
                    "Não há horários disponíveis nesse período. Escolha outro.\n\n"
                    "Digite 'voltar' para retornar."
                )

            self.session.set(
                self.sender_number,
                f"awaiting_slot:{employee_id}:{product_id}:{time_period}",
            )
            formatted = "\n".join(
                f"{i + 1}. {h}" for i, h in enumerate(options)
            )
            print("FORMATTED", formatted)
            print(type(formatted))
            self.session.set(f"{self.sender_number}_slots", options)

            chunks = [options[i : i + 6] for i in range(0, len(options), 6)]
            print("CHUNKS", chunks)
            result_message = ""
            for chunk_i, chunk in enumerate(chunks):
                formatted = "\n".join(
                    f"{i + 1 + chunk_i * 6}. {h}" for i, h in enumerate(chunk)
                )
                result_message += f"Horários disponíveis:\n{formatted}\n\n"
                print(
                    "RESULTADO COLETADO DENTRO DO RESULT MESSAGE",
                    result_message,
                )

            result_message += (
                "Digite o número desejado ou 'voltar' para retornar."
            )
            print(result_message)
            return result_message

        elif state.startswith("awaiting_slot"):
            if self.message == "voltar":
                _, employee_id, product_id, _ = state.split(":")
                self.session.set(
                    self.sender_number,
                    f"awaiting_time:{employee_id}:{product_id}",
                )
                return self.handle_schedule_flow()

            options = self.session.get(f"{self.sender_number}_slots") or []
            if not self.message.isdigit() or int(self.message) not in range(
                1, len(options) + 1
            ):
                return (
                    "Seleção inválida. Escolha um número da lista.\n\n"
                    "Digite 'voltar' para retornar."
                )

            _, employee_id, product_id, _ = state.split(":")
            user_id = self.identify_user()
            selected_time_str = options[int(self.message) - 1]
            today = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
            time_obj = datetime.strptime(selected_time_str, "%H:%M").time()
            datetime_obj = datetime.combine(today, time_obj).astimezone(
                ZoneInfo("UTC")
            )

            self.register_schedule(
                user_id, product_id, employee_id, datetime_obj
            )  # register shedule

        return self.session.reset_to_default(
            self.sender_number, RESPONSE_DICTIONARY
        )

    def cancel_schedule(self):
        if self.message == "menu":
            return self.session.reset_to_default(
                self.sender_number, RESPONSE_DICTIONARY
            )
        if not self.message.isdigit():
            return (
                "Por favor, informe um ID numérico válido do agendamento.\n\n"
                "Digite 'menu' para voltar ao início."
            )
        user_id = self.identify_user()
        if not user_id:
            self.session.set(self.sender_number, "awaiting_register_data")
            return "Erro: usuário não encontrado. Por favor, cadastre-se novamente digitando 2.\n\nDigite 'menu' para voltar ao início."
        try:
            stmt = delete(ScheduleService).where(
                ScheduleService.id == int(self.message),
                ScheduleService.user_id == user_id,
            )
            result = db.session.execute(stmt)
            db.session.commit()
            if result.rowcount:
                return self.session.reset_to_default(
                    self.sender_number,
                    {
                        "success": (
                            "✅ Agendamento cancelado com sucesso.\n\n"
                            + RESPONSE_DICTIONARY["default"]
                        )
                    },
                )
            return self.session.reset_to_default(
                self.sender_number,
                {
                    "error": (
                        "Agendamento não encontrado.\n\n"
                        + RESPONSE_DICTIONARY["default"]
                    )
                },
            )
        except Exception as e:
            db.session.rollback()
            logdb("error", message=f"Failed to cancel schedule: {e}")
            return self.session.reset_to_default(
                self.sender_number,
                {
                    "error": (
                        "Erro ao cancelar agendamento. Tente novamente.\n\n"
                        + RESPONSE_DICTIONARY["default"]
                    )
                },
            )
