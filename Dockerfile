# Usar uma imagem base com Python
FROM python:3.12-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Instalar dependências do sistema necessárias para compilar pacotes Python e PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar o arquivo de requisitos
COPY requirements.txt .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar arquivos necessários
COPY manage.py .
COPY gunicorn.conf.py .
COPY src/external.py .

# Expor a porta do Flask/Gunicorn
EXPOSE 8000

# Comando padrão (sobrescrito no docker-compose.yml)
CMD ["gunicorn", "--config", "gunicorn.conf.py", "-b", "0.0.0.0:8000", "manage:app"]