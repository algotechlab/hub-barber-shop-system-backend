# src/bot/core.py
import os

import re
import secrets
import requests
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from datetime import date, time, timedelta
from datetime import datetime
from sqlalchemy.orm import aliased
from sqlalchemy import insert, select, update, delete, func, or_, and_, exists
from werkzeug.security import generate_password_hash

from src.bot.response_dictionary import RESPONSE_DICTIONARY
from src.bot.users import RegisterUser
from src.bot.schedule import Scheduler
from src.db.database import db
from src.model.model import User, Employee, ScheduleService, Products
from src.service.redis import SessionManager
from src.utils.log import logdb
from src.utils.metadata import Metadata

load_dotenv()

URL_INSTANCE_EVOLUTION = (
    "http://localhost:8080/message/sendText/chatbot_barber"
)
EVOLUTION_APIKEY = "E79EDCBE56E7-4C9B-AF67-30939918CF3A"

RESPONSE_DICTIONARY = {
    "default": (
        "Olá, seja bem-vindo à nossa barbearia! 💈\n\n"
        "Como posso te ajudar hoje?\n"
        "1️⃣ Quero fazer um agendamento\n"
        "2️⃣ Quero me cadastrar\n"
        "3️⃣ Horários de atendimento\n"
        "4️⃣ Tenho uma dúvida\n"
        "5️⃣ Cancelar agendamento\n\n"
        "Digite o número da opção desejada ou envie 'menu' para voltar ao início."
    ),
    "cancelar": (
        "Por favor, informe o ID do agendamento que deseja cancelar.\n"
        "Digite 'menu' para voltar ao início."
    ),
}


RESPONSE_DICTIONARY_TIMES = {
    "default": (
        "Horários de atendimento:\n"
        "Segunda-feira: 08:00 - 18:00\n"
        "Terca-feira: 08:00 - 18:00\n"
        "Quarta-feira: 08:00 - 18:00\n"
        "Quinta-feira: 08:00 - 18:00\n"
        "Sexta-feira: 08:00 - 18:00\n"
        "Sábado: 08:00 - 18:00\n"
        "Domingo: Fechado\n\n"
        "Digite 'menu' para voltar ao início."
    ),
    "manha": ("08:00 - 12:00\n"),
    "tarde": ("13:00 - 18:00\n"),
    "noite": ("18:00 - 20:30\n"),
}


class BotCore:
    def __init__(self, message: str, sender_number: str, push_name: str):
        self.message = message.strip().lower()
        self.sender_number = sender_number
        self.push_name = push_name
        self.base_url = URL_INSTANCE_EVOLUTION
        self.apikey = EVOLUTION_APIKEY
        self.session = SessionManager()

    def get_response(self) -> str:
        try:
            # Comando global para resetar
            if self.message == "menu":
                return self.session.reset_to_default(
                    self.sender_number, RESPONSE_DICTIONARY
                )

            # Processar estados primeiro
            state = self.session.get(self.sender_number)
            if state:
                if state == "awaiting_register_data":
                    return RegisterUser(
                        self.message, self.sender_number, self.push_name
                    ).process()
                elif state == "awaiting_cancel_id":
                    return Scheduler(
                        self.message, self.sender_number
                    ).cancel_schedule()
                elif state in (
                    "registered",
                    "awaiting_employee",
                ) or state.startswith(("awaiting_product", "awaiting_time")):
                    return Scheduler(
                        self.message, self.sender_number
                    ).handle_schedule_flow()

            # Opção 1: Agendamento
            if self.message == "1":
                if not self.identify_user():
                    self.session.set(
                        self.sender_number, "awaiting_register_data"
                    )
                    return "Por favor, envie seu nome completo (nome e sobrenome).\n\nDigite 'menu' para voltar ao início."
                self.session.set(self.sender_number, "registered")
                return Scheduler(
                    self.message, self.sender_number
                ).handle_schedule_flow()

            # Opção 2: Cadastro
            elif self.message == "2":
                self.session.set(self.sender_number, "awaiting_register_data")
                return "Por favor, envie seu nome completo (nome e sobrenome).\n\nDigite 'menu' para voltar ao início."

            # Opção 3: Horários
            elif self.message == "3":
                return (
                    "Nossos horários de atendimento são:\n"
                    "Segunda a Sábado: 9h às 18h\n\n"
                    "Para agendar, digite 1.\nDigite 'menu' para voltar ao início."
                )

            # Opção 4: Dúvida
            elif self.message == "4":
                return (
                    "Envie sua dúvida que te ajudo! 😊\n\n"
                    "Digite 'menu' para voltar ao início."
                )

            # Opção 5: Cancelar agendamento
            elif self.message == "5":
                self.session.set(self.sender_number, "awaiting_cancel_id")
                return RESPONSE_DICTIONARY["cancelar"]

            # Fallback para mensagens inválidas
            return self.session.reset_to_default(
                self.sender_number, RESPONSE_DICTIONARY
            )
        except Exception as e:
            logdb("error", message=f"Failed to generate response: {e}")
            return self.session.reset_to_default(
                self.sender_number, RESPONSE_DICTIONARY
            )

    def identify_user(self):
        try:
            stmt = select(User.id).where(User.phone == self.sender_number)
            result = db.session.execute(stmt).fetchone()
            return result[0] if result else None
        except Exception as e:
            logdb("error", message=f"Failed to identify user: {e}")
            return None

    def send_message(self):
        try:
            payload = {
                "number": self.sender_number,
                "text": self.get_response(),
                "delay": 2000,
            }
            headers = {
                "apikey": self.apikey,
                "Content-Type": "application/json",
            }
            response = requests.post(
                self.base_url, json=payload, headers=headers, timeout=5
            )
            logdb(
                "debug",
                message=f"Sent message to {self.sender_number}: {response.status_code}, {response.text}",
            )
            return response
        except Exception as e:
            print("coletnado o erro 500", e)
            logdb("error", message=f"Failed to send message: {e}")
            return None
