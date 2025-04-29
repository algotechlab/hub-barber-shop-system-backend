# Usar uma imagem base com Python
FROM python:3.12-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Instalar dependências do sistema necessárias para compilar pacotes Python
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar o arquivo de requisitos
COPY requirements.txt .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar a pasta src/ (onde está o manage.py e o código do Django)
COPY src/ .

# Expor a porta do Django
EXPOSE 8000

# Comando padrão (sobrescrito no docker-compose.yml)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]