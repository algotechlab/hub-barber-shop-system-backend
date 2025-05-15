import requests

# 00F3EDEEAC4A-44E0-8410-D6500037D5C6
# 00F3EDEEAC4A-44E0-8410-D6500037D5C6


def send_whatsapp_message():
    url = "http://localhost:8080/message/sendText/chatbot_barber"
    headers = {
        "Content-Type": "application/json",
        "apikey": "00F3EDEEAC4A-44E0-8410-D6500037D5C6",
    }

    message_text = """Flaks ..."""

    payload = {
        "number": "5561993936908",
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
