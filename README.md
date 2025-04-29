# Projeto da barbearia DG


## Modelos de negócio

#### **Usuários**:

Para o cadastro de usuário é necessário o cadastro dele, onde vamos coletar o `nome`, `email`, `telefone`. Rastreabilidade de criação, edição e o deletar.

**Motivo?**

Usuário será o leed final da aplicação, onde será realizada uma prospecção de marketing para cadastro simples no `link` externo. Ele terá uma página responsável para escolher o produto e o profissional que está disponível.


```python
class User(models.Model):
    name = models.CharField(max_length=120 , blank=False, null=False)
    email = models.EmailField(max_length=100, blank=False, null=False)
    password = models.CharField(max_length=300, blank=False, null=False)
    phone = models.CharField(max_length=40, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.IntegerField(blank=True, null=True)
    deleted_by = models.IntegerField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<User name={self.name} email={self.email}>"
```


### Estrutura de projeto
```plaintext
├── barbershop_project/    # Configurações principais do
core:
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