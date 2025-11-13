import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Caminho raiz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa Base e models
from src.db.database import db as Base
from src.model import load_all_models

# Config do Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = os.getenv("SQLALCHEMY_DATABASE_URI_MIGRATIONS")
if not database_url:
    raise RuntimeError("SQLALCHEMY_DATABASE_URI_MIGRATIONS não encontrada no .env")

config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata
load_all_models()

def include_object(obj, name, type_, reflected, compare_to):
    if type_ != "table":
        return True

    schema = getattr(obj, "schema", None)
    full_name = f"{schema}.{name}" if schema else name
    return full_name

def run_migrations_online():
    """Rodar migrations em modo sync"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            include_object=include_object,
            include_schemas=True,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()