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

# Copiar o manage.py e o diretório src/external/
COPY manage.py .
COPY src/external/ external/

# Expor a porta do Flask
EXPOSE 5000

# Comando padrão (sobrescrito no docker-compose.yml)
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]