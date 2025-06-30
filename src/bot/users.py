# src/bot/users.py
import os
import re

from dotenv import load_dotenv
from sqlalchemy import insert

from src.bot.response_dictionary import RESPONSE_DICTIONARY
from src.db.database import db
from src.model.model import User
from src.service.redis import SessionManager
from src.utils.log import logdb

load_dotenv()

URL_WEBAPP = os.getenv("URL_WEBAPP")


class RegisterUser:
    def __init__(self, message: str, sender_number: str, push_name: str):
        self.message = message.strip().lower()
        self.sender_number = sender_number
        self.push_name = push_name
        self.session = SessionManager()

    def _validate_name(self, name: str) -> bool:
        return bool(
            re.match(r"^[A-Za-zÀ-ÿ\s]{2,}\s+[A-Za-zÀ-ÿ\s]{2,}$", name.strip())
        )

    def __handle_register_data(self) -> str:
        if self.message == "menu":
            return self.session.reset_to_default(
                self.sender_number, RESPONSE_DICTIONARY
            )
        if self._validate_name(self.message):
            try:
                stmt = insert(User).values(
                    username=self.push_name,
                    lastname=self.message,
                    phone=self.sender_number,
                )
                db.session.execute(stmt)
                db.session.commit()
                self.session.set(self.sender_number, "registered")
                return (
                    f"{self.push_name}: Cadastro concluído com sucesso! 🎉\n"
                    f"Para acessar nosso sistema, clique no link abaixo:\n{URL_WEBAPP}\n\n"
                    "Agora você pode marcar um horário digitando 1."
                )
            except Exception as e:
                db.session.rollback()
                logdb("error", message=f"Error saving user: {e}")
                return self.session.reset_to_default(
                    self.sender_number,
                    {
                        "error": (
                            "Erro ao salvar cadastro. Tente novamente.\n\n"
                            + RESPONSE_DICTIONARY["default"]
                        )
                    },
                )
        return "👥 Por favor, envie seu nome completo *(nome e sobrenome)* para realizar um agendamento.\n\nDigite 'menu' para voltar ao início."

    def process(self) -> str:
        return self.__handle_register_data()
