import requests
import logging

# Dicionário de respostas para opções do menu
RESPONSE_DICTIONARY = {
    "1": "Ótimo! Para marcar um corte, me diga o dia e horário que você prefere! 😊",
    "2": "Para fazer o cadastro, por favor, envie seu nome completo e CPF.",
    "3": "Horários disponíveis: Segunda a Sábado, das 9h às 18h. Qual horário você prefere?",
    "4": "Para outras informações, envie sua dúvida que te ajudo! 😊",
    "default": """Bem vindo sou assitente do barbearia DG! 😊 Como posso ajudar você hoje?
1 - Marcar um corte
2 - Fazer cadastro
3 - Ver horários disponíveis
4 - Outras informações
Responda com o número da opção desejada."""
}

class BotCore:
    def __init__(self):
        self.base_url = "http://localhost:8080/message/sendText/chatbot_barber"
        self.apikey = "4E1C45786428-4F17-8A85-E8790027B405"

    @staticmethod
    def get_response(message):
        """Processa a mensagem e retorna a resposta"""
        message = message.lower().strip()
        print(f"Processamento de mensagem {message}")
        return RESPONSE_DICTIONARY.get(message, RESPONSE_DICTIONARY["default"])

    def send_message(self, message, sender_number):
        payload = {
            "number": sender_number,
            "text": self.get_response(message=message),
            "delay": 2000,
        }
        headers = {
            "apikey": self.apikey,
            "Content-Type": "application/json"
        }
        response = requests.request("POST", self.base_url, json=payload, headers=headers)
        return response