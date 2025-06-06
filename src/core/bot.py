import os
import re
import secrets
import requests
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from datetime import date, time, timedelta
from datetime import datetime
from sqlalchemy import insert, select, update, delete, func, or_
from werkzeug.security import generate_password_hash

from src.db.database import db
from src.model.model import User, Employee, ScheduleService, Products
from src.service.redis import SessionManager
from src.utils.log import logdb
from src.utils.metadata import Metadata

load_dotenv()

URL_INSTANCE_EVOLUTION = "http://localhost:8080/message/sendText/chatbot_barber"
EVOLUTION_APIKEY = "E79EDCBE56E7-4C9B-AF67-30939918CF3A"
URL_WEBAPP = "http://192.168.1.7:5173/"

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
    "manha" : (
      "08:00 - 12:00\n"  
    ),
    "tarde": (
        "13:00 - 18:00\n"
    ),
    "noite": (
      "19:00" - "20:00" 
    )
}

class RegisterUser:
    def __init__(self, message: str, sender_number: str, push_name: str):
        self.message = message.strip().lower()
        self.sender_number = sender_number
        self.push_name = push_name
        self.session = SessionManager()

    def _validate_name(self, name: str) -> bool:
        return bool(re.match(r"^[A-Za-zÀ-ÿ\s]{2,}\s+[A-Za-zÀ-ÿ\s]{2,}$", name.strip()))

    def __generate_password(self) -> str:
        return secrets.token_hex(4)

    def __handle_register_data(self) -> str:
        if self.message == "menu":
            return self.session.reset_to_default(self.sender_number, RESPONSE_DICTIONARY)
        if self._validate_name(self.message):
            try:
                password = self.__generate_password()
                stmt = insert(User).values(
                    username=self.push_name,
                    lastname=self.message,
                    phone=self.sender_number,
                    password=generate_password_hash(password, method="scrypt"),
                )
                db.session.execute(stmt)
                db.session.commit()
                self.session.set(self.sender_number, "registered")
                return (
                    f"{self.push_name}: Cadastro concluído com sucesso! 🎉\n"
                    f"Sua senha é *{password}*\n\n"
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
                    }
                )
        return "Por favor, envie seu nome completo (nome e sobrenome).\n\nDigite 'menu' para voltar ao início."

    def process(self) -> str:
        return self.__handle_register_data()

class Scheduler:
    def __init__(self, message: str, sender_number: str):
        self.message = message.strip().lower()
        self.sender_number = sender_number
        self.session = SessionManager()

    def identify_user(self):
        try:
            stmt = select(User.id).where(User.phone == self.sender_number)
            result = db.session.execute(stmt).fetchone()
            return result[0] if result else None
        except Exception as e:
            logdb("error", message=f"Failed to identify user: {e}")
            return None

    
    
    def get_employees_slots(self):
        # TODO - realizar o get id de todos os funcionarios com o horario de intervalo de 20 min
        local_tz = ZoneInfo("America/Sao_Paulo")
        start = datetime.combine(datetime.today(), time(8, 0))
        end = datetime.combine(date.today(), time(23, 0))
        step = timedelta(minutes=20)

        hour_slots = []

        while start <= end:
            response, status = self.list_available_employees(hour=start)

            available = []

            try:
                payload = (
                    response.get_json()
                    if hasattr(response, "get_json")
                    else response
                )
                if isinstance(payload, dict) and "data" in payload:
                    available = [e["username"] for e in payload["data"]]
            except Exception as e:
                logdb(
                    "error",
                    message=f"Error extract employees {start}: {e}",
                )

            hour_slots.append(
                {
                    "time": start.astimezone(local_tz).strftime("%H:%M"),
                    "available": available,
                }
            )

            start += step




    def handle_schedule_flow(self):
        state = self.session.get(self.sender_number)

        # Comandos globais
        if self.message == "menu":
            return self.session.reset_to_default(self.sender_number, RESPONSE_DICTIONARY)

        # Verifica cadastro
        if not self.identify_user():
            self.session.set(self.sender_number, "awaiting_register_data")
            return "Você precisa se cadastrar primeiro. Envie seu nome completo (nome e sobrenome).\n\nDigite 'menu' para voltar ao início."

        if state == "registered":
            employees = self.get_employees()
            if not employees:
                return self.session.reset_to_default(
                    self.sender_number,
                    {
                        "error": (
                            "Não há barbeiros disponíveis no momento.\n\n"
                            + RESPONSE_DICTIONARY["default"]
                        )
                    }
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
            if not self._validate_employee(employee_id):
                return (
                    "ID de barbeiro inválido. Escolha um ID da lista.\n\n"
                    "Digite 'voltar' para retornar ou 'menu' para voltar ao início."
                )
            self.session.set(self.sender_number, f"awaiting_product:{employee_id}")
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
            if not self._validate_product(product_id):
                return (
                    "ID de serviço inválido. Escolha um ID da lista.\n\n"
                    "Digite 'voltar' para escolher outro barbeiro ou 'menu' para voltar ao início."
                )
            self.session.set(self.sender_number, f"awaiting_time:{employee_id}:{product_id}")
            return (
                "Qual período prefere? manhã, tarde ou noite?\n\n"
                "Digite 'voltar' para escolher outro serviço ou 'menu' para voltar ao início."
            )

        elif state.startswith("awaiting_time"):
            if self.message == "voltar":
                employee_id = state.split(":")[1]
                self.session.set(self.sender_number, f"awaiting_product:{employee_id}")
                return self.handle_schedule_flow()
            time = self.message
            """
            Está pegando a noite, oque temos que fazer realmente aqui é coletar a hora que ele pegar, mais com isso tem outra regra de negocio,
            se ele escolher noite, ele vai ter que escolher um horário de 19:00 a 20:00, se ele escolher tarde, ele vai ter que escolher um horário de 13:00 a 18:00,
            se ele escolher manhã, ele vai ter que escolher um horário de 08:00 a 12:00.
            
            Diposinbilidade:
                
            
        
            Coletando o erro apos o schedule service (psycopg2.errors.InvalidDatetimeFormat) invalid input syntax for type timestamp: "noite"
            LINE 1: ...r_id, is_check, is_awayalone, is_deleted) VALUES ('noite', '...            
            """
            if time not in ("manhã", "tarde", "noite"):
                return (
                    "Por favor, escolha entre manhã, tarde ou noite.\n\n"
                    "Digite 'voltar' para escolher outro serviço ou 'menu' para voltar ao início."
                )
            _, employee_id, product_id = state.split(":")
            user_id = self.identify_user()
            if not user_id:
                self.session.set(self.sender_number, "awaiting_register_data")
                return "Erro: usuário não encontrado. Por favor, cadastre-se novamente digitando 2.\n\nDigite 'menu' para voltar ao início."
            try:
                stmt = insert(ScheduleService).values(
                    product_id=product_id,
                    employee_id=employee_id,
                    user_id=user_id,
                    time_register=time,
                    is_awayalone=False,
                    is_check=True,
                )
                db.session.execute(stmt)
                db.session.commit()
                return self.session.reset_to_default(
                    self.sender_number,
                    {
                        "success": (
                            "✅ Agendamento realizado com sucesso!\n\n"
                            + RESPONSE_DICTIONARY["default"]
                        )
                    }
                )
            except Exception as e:
                print("Coletando o erro apos o schedule service", e)
                db.session.rollback()
                logdb("error", message=f"Failed to save schedule: {e}")
                return self.session.reset_to_default(
                    self.sender_number,
                    {
                        "error": (
                            "Erro ao realizar agendamento. Tente novamente.\n\n"
                            + RESPONSE_DICTIONARY["default"]
                        )
                    }
                )

        return self.session.reset_to_default(self.sender_number, RESPONSE_DICTIONARY)

    def cancel_schedule(self):
        if self.message == "menu":
            return self.session.reset_to_default(self.sender_number, RESPONSE_DICTIONARY)
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
                ScheduleService.user_id == user_id
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
                    }
                )
            return self.session.reset_to_default(
                self.sender_number,
                {
                    "error": (
                        "Agendamento não encontrado.\n\n"
                        + RESPONSE_DICTIONARY["default"]
                    )
                }
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
                }
            )

    def _validate_employee(self, employee_id: int) -> bool:
        try:
            stmt = select(Employee.id).where(
                Employee.id == employee_id,
                ~Employee.is_deleted
            )
            return db.session.execute(stmt).scalar() is not None
        except Exception as e:
            logdb("error", message=f"Failed to validate employee: {e}")
            return False

    def _validate_product(self, product_id: int) -> bool:
        try:
            stmt = select(Products.id).where(
                Products.id == product_id,
                ~Products.is_deleted
            )
            return db.session.execute(stmt).scalar() is not None
        except Exception as e:
            logdb("error", message=f"Failed to validate product: {e}")
            return False

    def get_employees(self):
        try:
            stmt = select(Employee.id, Employee.username).where(~Employee.is_deleted)
            result = db.session.execute(stmt).fetchall()
            metadata = Metadata(result).model_to_list()
            return "\n".join([f"{item['id']} - {item['username']}" for item in metadata])
        except Exception as e:
            logdb("error", message=f"Failed to get employees: {e}")
            return ""

    def get_products(self):
        try:
            stmt = select(Products.id, func.upper(Products.description).label("name")).where(~Products.is_deleted)
            result = db.session.execute(stmt).fetchall()
            metadata = Metadata(result).model_to_list()
            return "\n".join([f"{item['id']} - {item['name']}" for item in metadata])
        except Exception as e:
            logdb("error", message=f"Failed to get products: {e}")
            return ""

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
                return self.session.reset_to_default(self.sender_number, RESPONSE_DICTIONARY)

            # Processar estados primeiro
            state = self.session.get(self.sender_number)
            if state:
                if state == "awaiting_register_data":
                    return RegisterUser(self.message, self.sender_number, self.push_name).process()
                elif state == "awaiting_cancel_id":
                    return Scheduler(self.message, self.sender_number).cancel_schedule()
                elif state in ("registered", "awaiting_employee") or state.startswith(("awaiting_product", "awaiting_time")):
                    return Scheduler(self.message, self.sender_number).handle_schedule_flow()

            # Opção 1: Agendamento
            if self.message == "1":
                if not self.identify_user():
                    self.session.set(self.sender_number, "awaiting_register_data")
                    return "Por favor, envie seu nome completo (nome e sobrenome).\n\nDigite 'menu' para voltar ao início."
                self.session.set(self.sender_number, "registered")
                return Scheduler(self.message, self.sender_number).handle_schedule_flow()

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
            return self.session.reset_to_default(self.sender_number, RESPONSE_DICTIONARY)
        except Exception as e:
            logdb("error", message=f"Failed to generate response: {e}")
            return self.session.reset_to_default(self.sender_number, RESPONSE_DICTIONARY)

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
                self.base_url,
                json=payload,
                headers=headers,
                timeout=5
            )
            logdb("debug", message=f"Sent message to {self.sender_number}: {response.status_code}, {response.text}")
            return response
        except Exception as e:
            print("coletnado o erro 500", e)
            logdb("error", message=f"Failed to send message: {e}")
            return None