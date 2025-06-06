import requests


# 4E1C45786428-4F17-8A85-E8790027B405
def send_whatsapp_message():
    url = "http://localhost:8080/message/sendText/chatbot_barber"
    headers = {
        "Content-Type": "application/json",
        "apikey": "E79EDCBE56E7-4C9B-AF67-30939918CF3A",
    }

    message_text = """Flaks com 20% de desconto
    Link: https://www.google.com.br/"""

    payload = {
        "number": "5561994261245",
        "text": message_text,
        "options": {
            "delay": 100,
            "presence": "composing",
            "linkPreview": True,
        },
        "textMessage": {"text": message_text},
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print("Mensagem enviada com sucesso:", response.json())
    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP: {http_err} - {response.text}")
    except requests.exceptions.RequestException as e:
        print("Erro ao enviar mensagem:", e)


if __name__ == "__main__":
    send_whatsapp_message()
