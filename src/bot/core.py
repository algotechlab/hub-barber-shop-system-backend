# src/bot/core.py

import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv
from sqlalchemy import select

from src.bot.response_dictionary import RESPONSE_DICTIONARY, TIME_SLOTS_CONFIG
from src.bot.schedule import Scheduler
from src.bot.users import RegisterUser
from src.db.database import db
from src.model.model import User
from src.service.redis import SessionManager

load_dotenv()

URL_INSTANCE_EVOLUTION = os.getenv(
    "URL_INSTANCE_EVOLUTION",
    "http://localhost:8080/message/sendText/chatbot_barber",
)
# EVOLUTION_APIKEY = os.getenv("EVOLUTION_AP") # todo - adjust config instancie evolution api whatsapp

EVOLUTION_APIKEY = "CAF4D3F98976-485B-BC05-8880DDE44F94"


class BotCore:
    def __init__(self, message: str, sender_number: str, push_name: str):
        self.message = message.strip().lower()
        self.sender_number = sender_number
        self.push_name = push_name
        self.base_url = URL_INSTANCE_EVOLUTION
        self.apikey = EVOLUTION_APIKEY
        self.session = SessionManager()
        self.scheduler = Scheduler(self.message, self.sender_number)

    def _handle_state_flow(self, state: str) -> str:
        """Gerencia o fluxo baseado no estado atual do usuário"""
        print(f"DEBUG: Handling state {state} for {self.sender_number}")
        state_handlers = {
            "undefined": self._handle_registration,
            "awaiting_cancel_id": self._handle_cancellation,
            "awaiting_period_selection": self._handle_period_selection,
            "awaiting_time_slot": self._handle_time_slot_selection,
            "awaiting_employee": self.scheduler.handle_schedule,
            "awaiting_product": self.scheduler.handle_schedule,
            "awaiting_period": self._handle_period_selection,
            "awaiting_slot": self.scheduler.handle_schedule,
        }
        for handler_state, handler in state_handlers.items():
            if state == handler_state or state.startswith(handler_state + ":"):
                try:
                    return handler()
                except Exception as e:
                    print(f"ERROR: Error handling state {state}: {e}")
                    return self._reset_session()
        print(f"WARNING: Unknown state {state} for {self.sender_number}")
        return self._reset_session()

    def _get_occupied_slots(self, period: str) -> list:
        """Recupera horários ocupados para um período específico"""
        try:
            employee_id = self.session.get(f"{self.sender_number}_employee_id")
            if not employee_id:
                print(
                    f"WARNING: No employee_id found for {self.sender_number}"
                )
                return []

            employee_id = int(employee_id)
            occupied_slots = self.scheduler._get_occupied_slots(
                period, employee_id
            )
            print(f"DEBUG: Coletando occupied_slots {occupied_slots}")
            return occupied_slots
        except Exception as e:
            print(f"ERROR: Failed to get occupied slots for {period}: {e}")
            return []

    def _generate_time_slots_message(self, period: str) -> str:
        """Gera mensagem com horários disponíveis"""
        config = TIME_SLOTS_CONFIG.get(period)
        if not config:
            print(f"ERROR: Invalid period: {period}")
            return "Período inválido. Escolha entre manhã, tarde ou noite."

        occupied_slots = self._get_occupied_slots(period)
        available_slots = [
            slot for slot in config["slots"] if slot not in occupied_slots
        ]

        if not available_slots:
            print(f"WARNING: No available slots for {period}")
            return f"Não há horários disponíveis para {config['label']}. Escolha outro período.\n\nDigite 'menu' para voltar ao início."

        slots_message = "\n".join(
            f"{i + 1}. {slot}" for i, slot in enumerate(available_slots)
        )
        print(f"DEBUG: Available slots for {period}: {slots_message}")
        self.session.set(
            f"{self.sender_number}_slots", json.dumps(available_slots)
        )
        return (
            f"Horários disponíveis para {config['label']} ({config['period']}):\n"
            f"{slots_message}\n\n"
            "Digite o número do horário desejado ou 'menu' para voltar ao início."
        )

    def _handle_time_slot_selection(self) -> str:
        """Processa a seleção do horário específico"""
        scheduler_state = self.session.get(
            f"{self.sender_number}_scheduler_state"
        )
        if not scheduler_state or ":" not in scheduler_state:
            print(
                f"ERROR: Invalid scheduler state for {self.sender_number}: {scheduler_state}"
            )
            return self._reset_session()

        try:
            _, employee_id, product_id = scheduler_state.split(":")
            period = (
                self.session.get(f"{self.sender_number}_selected_period") or ""
            )
            if not period:
                print(f"ERROR: No period found for {self.sender_number}")
                return self._reset_session()

            config = TIME_SLOTS_CONFIG.get(period)
            if not config:
                print(f"ERROR: Invalid period config for {period}")
                return self._reset_session()

            slot_index = int(self.message) - 1
            slots_json = (
                self.session.get(f"{self.sender_number}_slots") or "[]"
            )
            available_slots = json.loads(slots_json)

            if slot_index < 0 or slot_index >= len(available_slots):
                print(
                    f"WARNING: Invalid slot index {self.message} for {self.sender_number}"
                )
                return "Opção inválida. Digite um número válido do horário."

            selected_time = available_slots[slot_index]

            self.session.set(
                self.sender_number,
                f"awaiting_slot:{employee_id}:{product_id}:{period}",
            )
            print(
                f"DEBUG: Set state to awaiting_slot:{employee_id}:{product_id}:{period}, selected time {selected_time} for {self.sender_number}"
            )

            return self._continue_schedule_flow(period, selected_time)
        except ValueError:
            print(
                f"WARNING: Non-numeric input for slot selection: {self.message}"
            )
            return "Por favor, digite apenas o número do horário desejado."
        except json.JSONDecodeError as e:
            print(
                f"ERROR: Failed to decode slots JSON for {self.sender_number}: {e}"
            )
            return self._reset_session()

    def _handle_period_selection(self) -> str:
        """Processa a seleção do período (manhã, tarde, noite)"""
        period_map = {"1": "manha", "2": "tarde", "3": "noite"}
        selected_period = period_map.get(self.message)
        if not selected_period:
            print(f"WARNING: Invalid period selection: {self.message}")
            return "Opção inválida. " + RESPONSE_DICTIONARY["period_selection"]

        self.session.set(
            f"{self.sender_number}_selected_period", selected_period
        )
        self.session.set(self.sender_number, "awaiting_time_slot")
        print(
            f"DEBUG: Set state to awaiting_time_slot, period {selected_period} for {self.sender_number}"
        )
        return self._generate_time_slots_message(selected_period)

    def get_response(self) -> str:
        try:
            if self.message == "menu":
                print(
                    f"DEBUG: User requested menu, resetting state for {self.sender_number}"
                )
                return self._reset_session()

            state = self.session.get(self.sender_number)
            print(f"DEBUG: Current state for {self.sender_number}: {state}")

            if state and state.startswith("awaiting_slot"):
                print(
                    f"DEBUG: Forcing session reset due to awaiting_slot state {state} for {self.sender_number}"
                )
                self._reset_session()
                state = None

            if state:
                return self._handle_state_flow(state)

            if self.message == "1":
                if not self.identify_user():
                    self.session.set(self.sender_number, "undefined")
                    print(
                        f"DEBUG: User not identified, set state to undefined for {self.sender_number}"
                    )
                    return "Por favor, envie seu nome completo (nome e sobrenome).\n\nDigite 'menu' para voltar ao início."
                self.session.set(self.sender_number, "undefined")
                print(
                    f"DEBUG: Set state to undefined for {self.sender_number}"
                )
                return self.scheduler.handle_schedule()

            elif self.message == "2":
                self.session.set(self.sender_number, "undefined")
                print(
                    f"DEBUG: Set state to undefined for {self.sender_number}"
                )
                return "Por favor, envie seu nome completo (nome e sobrenome).\n\nDigite 'menu' para voltar ao início."

            elif self.message == "3":
                print(
                    f"DEBUG: User requested operating hours for {self.sender_number}"
                )
                return (
                    "Nossos horários de atendimento são:\n"
                    "Segunda a Sábado: 9h às 18h\n\n"
                    "Para agendar, digite 1.\nDigite 'menu' para voltar ao início."
                )

            elif self.message == "4":
                print(
                    f"DEBUG: User requested support for {self.sender_number}"
                )
                return (
                    "Envie sua dúvida que te ajudo! 😊\n\n"
                    "Digite 'menu' para voltar ao início."
                )

            elif self.message == "5":
                self.session.set(self.sender_number, "awaiting_cancel_id")
                print(
                    f"DEBUG: Set state to awaiting_cancel_id for {self.sender_number}"
                )
                return self.scheduler.cancel_schedule()

            elif self.message == "6":
                print(
                    f"DEBUG: User requested their schedules for {self.sender_number}"
                )
                return self.scheduler.list_schedules()

            print(
                f"DEBUG: No valid option selected, resetting to default for {self.sender_number}"
            )
            return self._reset_session()
        except Exception as e:
            print(f"ERROR: Failed to generate response: {e}")
            return self._reset_session()

    def _continue_schedule_flow(self, period: str, selected_time: str) -> str:
        """Continua o fluxo de agendamento após seleção do horário"""
        config = TIME_SLOTS_CONFIG.get(period)
        if not config:
            print(f"ERROR: Invalid period in continue_schedule_flow: {period}")
            return self._reset_session()

        state = self.session.get(f"{self.sender_number}_scheduler_state")
        if not state or ":" not in state:
            print(
                f"ERROR: Invalid scheduler state for {self.sender_number}: {state}"
            )
            return self._reset_session()

        try:
            _, employee_id, product_id = state.split(":")
            user_id = self.identify_user()
            if not user_id:
                self.session.set(self.sender_number, "undefined")
                print(
                    f"ERROR: User not found, set state to undefined for {self.sender_number}"
                )
                return "Erro: usuário não encontrado. Por favor, cadastre-se novamente.\n\nDigite 'menu' para voltar ao início."

            today = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
            time_obj = datetime.strptime(selected_time, "%H:%M").time()
            datetime_obj = datetime.combine(today, time_obj).astimezone(
                ZoneInfo("UTC")
            )
            result = self.scheduler.register_schedule(
                user_id, product_id, employee_id, datetime_obj
            )
            print(
                f"DEBUG: Register schedule result for {self.sender_number}: {result}"
            )
            return result
        except Exception as e:
            print(
                f"ERROR: Failed to register schedule for {self.sender_number}: {e}"
            )
            return (
                "Erro ao registrar agendamento. Tente novamente.\n\n"
                + RESPONSE_DICTIONARY["default"]
            )

    def identify_user(self):
        try:
            stmt = select(User.id).where(User.phone == self.sender_number)
            result = db.session.execute(stmt).fetchone()
            print(
                f"DEBUG: User lookup for {self.sender_number}: {'Found' if result else 'Not found'}"
            )
            return result[0] if result else None
        except Exception as e:
            print(f"ERROR: Failed to identify user: {e}")
            return None

    def _handle_registration(self) -> str:
        return RegisterUser(
            self.message, self.sender_number, self.push_name
        ).process()

    def _handle_cancellation(self) -> str:
        return self.scheduler.cancel_schedule()

    def _reset_session(self) -> str:
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
            return RESPONSE_DICTIONARY["default"]
        except Exception as e:
            print(
                f"ERROR: Failed to reset session for {self.sender_number}: {e}"
            )
            return RESPONSE_DICTIONARY["default"]

    def send_message(self):
        try:
            response_text = self.get_response()
            payload = {
                "number": self.sender_number,
                "text": response_text,
                "delay": 2000,
            }
            headers = {
                "apikey": self.apikey,
                "Content-Type": "application/json",
            }
            print(f"DEBUG: Sending payload to {self.sender_number}: {payload}")
            response = requests.post(
                self.base_url, json=payload, headers=headers, timeout=5
            )
            print(
                f"DEBUG: Sent message to {self.sender_number}: {response.status_code}, {response.text}"
            )
            if response.status_code != 201:
                print(
                    f"ERROR: Failed to send message to {self.sender_number}: {response.status_code}, {response.text}"
                )
            return response
        except Exception as e:
            print(f"ERROR: Failed to send message: {e}")
            return None
