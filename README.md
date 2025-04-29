# barbershop_project

Estrutura do `barbershop_project`

```plaintext
barbershop_project/
│
├── manage.py
├── README.md
├── requirements.txt
├── .env.example
│
├── barbershop_project/    # Configurações principais do projeto
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py        # Configurações comuns
│   │   ├── dev.py         # Configurações de desenvolvimento
│   │   ├── prod.py        # Configurações de produção
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── users/             # Cadastro, login, reset de senha
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── forms.py
│   ├── products/          # Gestão de cortes, produtos
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── serializers.py
│   │   └── admin.py
│   ├── appointments/      # Agendamentos de horários
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services.py
│   ├── campaigns/         # Campanhas de marketing
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── admin.py
│   └── core/              # Funções utilitárias (helpers)
│       ├── services.py
│       ├── utils.py
│       └── validations.py
│
├── templates/             # Django Templates (se precisar)
├── static/                # Imagens, CSS, JS
└── media/                 # Uploads dos usuários
```