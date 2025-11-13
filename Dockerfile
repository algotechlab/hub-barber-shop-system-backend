# Etapa de build (para compilar dependências)
FROM python:3.12-slim AS builder

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install --no-cache-dir poetry>=1.8.0

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de configuração do Poetry
COPY pyproject.toml poetry.lock ./

# Instalar dependências de produção (sem dev/test)
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --no-root

# ---------------------------------------------------------------------
# Etapa final (runtime)
FROM python:3.12-slim

# Instalar dependências mínimas de runtime
RUN apt-get update && apt-get install -y \
    libpq5 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar dependências instaladas da etapa de build
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar o código da aplicação
COPY . .

# Expor a porta
EXPOSE 8000

# Comando padrão (pode ser sobrescrito no docker-compose)
CMD ["gunicorn", "--config", "gunicorn.conf.py", "--bind", "0.0.0.0:8000", "manage:app"]