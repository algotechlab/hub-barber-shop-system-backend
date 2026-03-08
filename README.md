# Hub Barber Shop System Backend

API backend para gestão de barbearia, incluindo autenticação, cadastro de entidades de negócio, agenda e integrações externas.

## Visão Geral

Este projeto implementa uma API com `FastAPI`, organizada em arquitetura por camadas, com foco em:

- domínio desacoplado de infraestrutura;
- testes unitários abrangentes;
- migrações com `Alembic`;
- execução local e com `Docker`.

## Stack Tecnológica

- `Python 3.13`
- `FastAPI`
- `SQLAlchemy` (assíncrono com `asyncpg`)
- `PostgreSQL`
- `Alembic`
- `Poetry`
- `Pytest` + `pytest-cov`
- `Ruff`
- `Docker` + `docker-compose`

## Arquitetura do Projeto

Estrutura principal:

- `src/core`: configurações globais, segurança e utilitários.
- `src/domain`: regras de negócio (DTOs, serviços, casos de uso, interfaces de repositório e exceções).
- `src/infrastructure`: banco, repositórios concretos, integrações externas e storage.
- `src/interface`: camada HTTP (rotas, schemas, controllers, dependencies e middlewares).
- `migrations`: histórico de migrações do banco.
- `tests`: suíte de testes unitários por camada.

O bootstrap da API acontece em `src/main.py`, que:

- configura CORS;
- registra handlers de exceções;
- carrega modelos do banco;
- inclui o roteador principal em `/api/v1`.

## Endpoints Principais

As rotas são carregadas dinamicamente a partir de `src/interface/api/v1/routes`.

Base path: `/api/v1`

- `/auth`
- `/owners`
- `/employees`
- `/users`
- `/company`
- `/services`
- `/products`
- `/schedule`
- `/schedule-blocks`
- `/market-paid`
- `/slug-companies`

Documentação interativa:

- Swagger: `/docs` (habilitado quando `DEBUG=true`)
- ReDoc: `/redoc` (habilitado quando `DEBUG=true`)

## Pré-requisitos

- `Python 3.13`
- `Poetry`
- `Docker` e `docker-compose` (opcional, recomendado para ambiente completo)
- `PostgreSQL` (caso rode sem Docker)

## Configuração do Ambiente

1. Clone o repositório:

```bash
git clone <url-do-repositorio>
cd hub-barber-shop-system-backend
```

2. Crie seu arquivo de ambiente:

```bash
cp env.example.env .env
```

3. Ajuste variáveis importantes no `.env`:

- `API_PORT`
- `DEBUG`
- `BACKEND_CORS_ORIGINS`
- `SQLALCHEMY_DATABASE_URI` (ou use `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME`)
- `JWT_SECRET`
- credenciais `AWS_*` (se for usar upload em S3)
- `MARKET_PAID_ACCESS_TOKEN` (se for usar integração Mercado Pago)

## Rodando com Docker

Suba banco + API:

```bash
docker-compose up --build
```

Comportamento esperado:

- Postgres sobe no serviço `barbersystem_database`;
- aplicação sobe no serviço `fast_api_barber_shop_system_backend`;
- migrações são executadas no startup via `entrypoints/init-db.sh`;
- API disponível em `http://localhost:${API_PORT}`.

## Rodando Localmente (sem Docker)

1. Instale dependências:

```bash
poetry install --with dev
```

2. Execute migrações:

```bash
poetry run alembic upgrade head
```

3. Suba a aplicação:

```bash
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Migrações

Aplicar migrações:

```bash
poetry run alembic upgrade head
```

Criar nova migração:

```bash
poetry run alembic revision --autogenerate -m "descricao_da_migracao"
```

## Qualidade de Código e Testes

Lint e formatação:

```bash
poetry run task lint
```

Testes:

```bash
poetry run task test
```

Somente suíte unitária:

```bash
poetry run task test_unit
```

O projeto possui configuração rigorosa de cobertura em `pyproject.toml`, com meta alta de cobertura para manter segurança em refactors.

## CI

Pipeline em `.github/workflows/python-app.yml` executa:

- instalação de dependências;
- lint;
- testes unitários com cobertura.

## Observações Importantes

- A versão de Python alvo do projeto é `3.13`.
- Em ambiente Docker, a API recebe `SQLALCHEMY_DATABASE_URI` apontando para o serviço do banco na rede interna.
- O carregamento de rotas `v1` é dinâmico: novos módulos em `src/interface/api/v1/routes` com `router` são incluídos automaticamente.

## Licença

Este projeto está sob a licença definida em `LICENSE`.
