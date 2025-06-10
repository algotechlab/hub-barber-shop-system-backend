# src/bot/response_dictionary.py
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
