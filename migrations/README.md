Comando de migração

```sh
alembic revision --autogenerate -m "Add phone in models user"
```

Aplicar migrações no banco (inclui colunas novas como `schedule_finance.service_id`):

```sh
alembic upgrade head
```

Se aparecer erro de coluna inexistente no runtime, o banco está atrás do código — rode `alembic upgrade head` no mesmo ambiente do `.env`.

**Schema Postgres:** as revisões antigas criam tabelas no schema padrão (em geral `public`). Se no `.env` você usa `POSTGRES_SCHEMA=barbersystem`, esse schema precisa existir no Postgres (`CREATE SCHEMA IF NOT EXISTS barbersystem;`) ou use `POSTGRES_SCHEMA=public` quando as tabelas estiverem em `public`.