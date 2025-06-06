import os
import re
import secrets

import requests
from dotenv import load_dotenv
from sqlalchemy import insert
from werkzeug.security import generate_password_hash

from src.db.database import db
from src.model.model import User
from src.service.redis import SessionManager
from src.utils.log import logdb

load_dotenv()

URL_INSTANCE_EVOLUTION = os.getenv("URL_INSTANCE_EVOLUTION")
EVOLUTION_APIKEY = os.getenv("EVOLUTION_APIKEY")
URL_WEBAPP = os.getenv("URL_WEBAPP")

RESPONSE_DICTIONARY = {
    "1": (
        "Ótimo! Para marcar um corte, me diga o dia e horário que você "
        "prefere! 😊"
    ),
    "2": (
        "Para fazer o cadastro, por favor, envie seu nome completo (nome "
        "e sobrenome)."
    ),
    "3": (
        "Horários disponíveis: Segunda a Sábado, das 9h às 18h. "
        "Qual horário você prefere?"
    ),
    "4": ("Para outras informações, envie sua dúvida que te ajudo! 😊"),
    "default": (
        "Bem-vindo! Sou a assistente da barbearia DG! 😊 Como posso ajudar "
        "você hoje?\n"
        "1 - Marcar um corte\n"
        "2 - Fazer cadastro\n"
        "3 - Ver horários disponíveis\n"
        "4 - Outras informações\n"
        "Responda com o número da opção desejada."
    ),
}


class RegisterUser:
    def __init__(self, message: str, sender_number: str, push_name: str):
        self.message = message.strip().lower()
        self.sender_number = sender_number
        self.push_name = push_name
        self.session = SessionManager()
        self.user = User

    def _validate_name(self, name: str) -> bool:
        return bool(
            re.match(r"^[A-Za-zÀ-ÿ\s]{2,}\s+[A-Za-zÀ-ÿ\s]{2,}$", name.strip())
        )

    def __generate_password(self) -> str:
        return secrets.token_hex(4)

    def __handle_register_confirm(self) -> str:
        if self.message in ("sim", "s"):
            self.session.set(self.sender_number, "registered")
            return RESPONSE_DICTIONARY["1"]
        if self.message in ("não", "nao", "n"):
            self.session.set(self.sender_number, "awaiting_register_data")
            return RESPONSE_DICTIONARY["2"]
        return "Por favor, responda com 'sim' ou 'não'."

    def __handle_register_data(self) -> str:
        if self._validate_name(self.message):
            self.session.set(self.sender_number, "registered")
            password = self.__generate_password()
            stmt = insert(self.user).values(
                username=self.push_name,
                lastname=self.message,
                phone=self.sender_number,
                password=generate_password_hash(password, method="scrypt"),
            )
            db.session.execute(stmt)
            db.session.commit()
            return (
                f"{self.push_name}: Cadastro concluído com sucesso! 🎉\n"
                f"Sua senha é *{password}*\n\n"
                f"Para acessar nosso sistema, clique no link abaixo:\n"
                f"{URL_WEBAPP}\n\n"
                f"Agora você pode marcar um horário digitando 1."
            )
        return "Por favor, envie seu nome completo (nome e sobrenome)."

    def process(self) -> str:
        try:
            current_state = self.session.get(self.sender_number)

            if current_state == "awaiting_register_confirm":
                return self.__handle_register_confirm()

            if current_state == "awaiting_register_data":
                return self.__handle_register_data()

            return None

        except Exception as e:
            logdb("error", message=f"Erro ao processar cadastro: {e}")
            return (
                "Ocorreu um erro durante o cadastro. "
                "Tente novamente mais tarde."
            )


class BotCore:
    def __init__(self, message: str, sender_number: str, push_name: str):
        self.message = message.strip().lower()
        self.sender_number = sender_number
        self.push_name = push_name
        self.base_url = os.getenv("URL_INSTANCE_EVOLUTION")
        self.apikey = os.getenv("EVOLUTION_APIKEY")
        self.session = SessionManager()
        self.user = User

    def get_response(self) -> str:
        try:
            # Fluxo "1" - Marcar corte → inicia pergunta se tem cadastro
            if self.message == "1":
                self.session.set(
                    self.sender_number, "awaiting_register_confirm"
                )
                return (
                    "Para realizar o corte é necessário um cadastro.\n"
                    "Você já tem? (sim/não)"
                )

            # Fluxo "2" → inicia cadastro diretamente
            elif self.message == "2":
                self.session.set(self.sender_number, "awaiting_register_data")
                return (
                    "Por favor, envie seu nome completo\n"
                    "(nome e sobrenome)."
                )

            # Processa interações de estado
            current_state = self.session.get(self.sender_number)
            if current_state:
                return RegisterUser(
                    self.message, self.sender_number, self.push_name
                ).process()

            # Demais opções
            return RESPONSE_DICTIONARY.get(
                self.message, RESPONSE_DICTIONARY["default"]
            )

        except Exception as e:
            logdb("error", message=f"Erro ao gerar resposta: {e}")
            return (
                "Desculpe,\n"
                "ocorreu um erro ao processar sua solicitação."
            )

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
                self.base_url, json=payload, headers=headers
            )
            return response
        except Exception as e:
            logdb("error", message=f"Erro ao enviar mensagem: {e}")
            return None
