"""
Seed de desenvolvimento: bootstrap do domínio (owner, company, colaboradores,
perfil, filial, serviços, produtos, planos, marketing, Mercado Pago, assinaturas,
bloqueios, caixa) e volume sintético de agendamentos, financeiro e despesas.

Uso (na raiz do projeto, com variáveis de ambiente e migrations aplicados):

  poetry run python -m src.infrastructure.seed.seed_metrics
  poetry run python -m src.infrastructure.seed.seed_metrics --mode bootstrap
  poetry run python -m src.infrastructure.seed.seed_metrics --mode metrics

Credenciais padrão do seed (clientes, funcionários e owner criados aqui)::

  senha: SeedDev123!

Ajuste ``COMPANY_ID`` e ``EMPLOYEES`` se a sua base já tiver outra company alvo;
caso a company ``COMPANY_ID`` não exista, o bootstrap cria owner + company com
o slug informado.
"""

from __future__ import annotations

import argparse
import asyncio
import random
from datetime import date, datetime, time, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from uuid import UUID

from faker import Faker
from sqlalchemy import insert, select

from src.core.utils.get_argon import hash_password
from src.infrastructure.database import load_all_models
from src.infrastructure.database.models.branch_companies import BranchCompany
from src.infrastructure.database.models.cash_register import (
    CashRegisterAdjustment,
    CashRegisterSession,
)
from src.infrastructure.database.models.commom.cash_movement_kind import (
    CashMovementKind,
)
from src.infrastructure.database.models.commom.employee_status import EmployeeRole
from src.infrastructure.database.models.commom.payment_method import PaymentMethod
from src.infrastructure.database.models.commom.payment_status import PaymentStatus
from src.infrastructure.database.models.commom.user_subscription_status import (
    UserSubscriptionStatus,
)
from src.infrastructure.database.models.companies import Company
from src.infrastructure.database.models.employees import Employee
from src.infrastructure.database.models.expense import Expense
from src.infrastructure.database.models.market_paid import MarketPaid
from src.infrastructure.database.models.owner import Owner
from src.infrastructure.database.models.product import Product
from src.infrastructure.database.models.profile import Profile
from src.infrastructure.database.models.schedule import Schedule
from src.infrastructure.database.models.schedule_block import ScheduleBlock
from src.infrastructure.database.models.schedule_finance import ScheduleFinance
from src.infrastructure.database.models.service import Service
from src.infrastructure.database.models.subscription_plan import SubscriptionPlan
from src.infrastructure.database.models.subscription_plan_junctions import (
    subscription_plan_service_table,
)
from src.infrastructure.database.models.template_marketing import TemplateMarketingModel
from src.infrastructure.database.models.user_subscription import UserSubscription
from src.infrastructure.database.models.users import User
from src.infrastructure.database.session import get_session_factory

# --- Identificadores e catálogo fixo (reprodutível) --------------------------
COMPANY_ID = UUID('129d8d2d-0828-47a9-b586-8088c33eae8f')
COMPANY_SLUG = 'hub-barber-seed'
COMPANY_NAME = 'Barbearia Hub (Seed)'

# Email único do owner; troque se colidir com dados locais.
OWNER_EMAIL = 'owner.seed@hubbarber.local'

# (employee_id, primeiro_nome) — alinhado ao time real quando possível
EMPLOYEES = [
    (UUID('8670fbed-63ca-4046-aaf8-6eb48dcf180e'), 'Hedris'),
    (UUID('cdc28bc7-3cb8-423e-86f2-689591726adb'), 'Henrique'),
    (UUID('98de56cf-7197-49b3-a63c-ede4def98872'), 'Todas'),
    (UUID('d54667fb-82f3-479a-9324-aae32b6d7ae9'), 'Fabin'),
    (UUID('89a46fed-d9fc-4dd8-bea6-f20aa9dff25f'), 'Nilson'),
]

SEED_DEV_PASSWORD = 'SeedDev123!'
RANDOM_SEED = 20_260_311
METRICS_DAYS_WINDOW = 60
TARGET_SCHEDULES_PER_EMPLOYEE = 28
TARGET_EXPENSES = 22
TARGET_USERS = 35
MAX_USERS_PER_EMPLOYEE = 18
PRODUCT_USAGE_PROBABILITY = 0.45
DISCOUNT_USAGE_PROBABILITY = 0.28
PAYMENT_PAID_PROBABILITY = 0.90

# Perfil / UI
PROFILE_COLORS = ('#1a1a2e', '#16213e', '#0f3460', '#e94560', '#533483')


class SeedMode(StrEnum):
    full = 'full'
    bootstrap = 'bootstrap'
    metrics = 'metrics'


def money(value: Decimal | float | int) -> Decimal:
    return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def build_faker() -> Faker:
    """Faker em pt-BR, reprodutível com RANDOM_SEED."""
    random.seed(RANDOM_SEED)
    f = Faker('pt_BR')
    f.seed_instance(RANDOM_SEED)
    return f


# --- Bootstrap ----------------------------------------------------------------


async def ensure_owner_and_company(session) -> Company:
    existing = await session.get(Company, COMPANY_ID)
    if existing is not None:
        return existing

    owner = Owner(
        name='Dono (Seed)',
        email=OWNER_EMAIL,
        phone='11900000001',
        password=hash_password(SEED_DEV_PASSWORD),
    )
    session.add(owner)
    await session.flush()

    company = Company(
        id=COMPANY_ID,
        name=COMPANY_NAME,
        slug=COMPANY_SLUG,
        is_active=True,
        owner_id=owner.id,
    )
    session.add(company)
    await session.flush()
    return company


async def ensure_branch(session) -> None:
    q = select(BranchCompany).where(
        BranchCompany.company_id == COMPANY_ID,
        BranchCompany.is_deleted.is_(False),
    )
    r = await session.execute(q)
    if r.scalars().first() is not None:
        return
    session.add(
        BranchCompany(
            name='Matriz',
            company_id=COMPANY_ID,
        )
    )
    await session.flush()


async def ensure_catalog_employees(session) -> list[Employee]:
    """Cria colaboradores com os UUIDs de EMPLOYEES, se ainda não existirem."""
    out: list[Employee] = []
    for index, (emp_id, first_name) in enumerate(EMPLOYEES, start=1):
        row = await session.get(Employee, emp_id)
        if row is not None:
            out.append(row)
            continue
        phone = f'11{9 + index % 2:1d}9000{index:04d}'[:30]
        emp = Employee(
            id=emp_id,
            name=first_name,
            last_name='Sobrenome',
            phone=phone,
            password=hash_password(SEED_DEV_PASSWORD),
            is_active=True,
            role=EmployeeRole.role_employee.value,
            start_time=time(8, 30),
            end_time=time(21, 0),
            company_id=COMPANY_ID,
        )
        session.add(emp)
        out.append(emp)
    await session.flush()
    return out


async def ensure_profiles(session, employees: list[Employee]) -> int:
    q = select(Profile.employee_id).where(
        Profile.company_id == COMPANY_ID,
        Profile.is_deleted.is_(False),
    )
    r = await session.execute(q)
    have = set(r.scalars().all())
    created = 0
    for index, employee in enumerate(employees):
        if employee.id in have:
            continue
        color = PROFILE_COLORS[index % len(PROFILE_COLORS)]
        phone = f'11{9 + (index % 2):1d}9000{index:04d}00'[:20]
        session.add(
            Profile(
                color=color,
                phone=phone,
                employee_id=employee.id,
                company_id=COMPANY_ID,
            )
        )
        created += 1
    if created:
        await session.flush()
    return created


async def get_or_create_services(session) -> list[Service]:
    query = select(Service).where(
        Service.company_id == COMPANY_ID,
        Service.is_deleted.is_(False),
    )
    result = await session.execute(query)
    services = list(result.scalars().all())
    if services:
        return services

    base_services = [
        Service(
            name='Corte Social',
            description='Corte tradicional',
            price=money('45'),
            duration=45,
            category='corte',
            time_to_spend=timedelta(minutes=45),
            status=True,
            url_image='https://placehold.co/600x400/png',
            company_id=COMPANY_ID,
        ),
        Service(
            name='Barba Completa',
            description='Barba na navalha',
            price=money('35'),
            duration=30,
            category='barba',
            time_to_spend=timedelta(minutes=30),
            status=True,
            url_image='https://placehold.co/600x400/png',
            company_id=COMPANY_ID,
        ),
        Service(
            name='Combo Corte+Barba',
            description='Pacote completo',
            price=money('70'),
            duration=60,
            category='combo',
            time_to_spend=timedelta(minutes=60),
            status=True,
            url_image='https://placehold.co/600x400/png',
            company_id=COMPANY_ID,
        ),
    ]
    session.add_all(base_services)
    await session.flush()
    return base_services


async def get_or_create_products(session) -> list[Product]:
    query = select(Product).where(
        Product.company_id == COMPANY_ID,
        Product.is_deleted.is_(False),
    )
    result = await session.execute(query)
    products = list(result.scalars().all())
    if products:
        return products

    base_products = [
        Product(
            name='Pomada Modeladora',
            description='Fixação média',
            price=money('29.90'),
            category='acabamento',
            company_id=COMPANY_ID,
            status=True,
            url_image='https://placehold.co/600x400/png',
        ),
        Product(
            name='Óleo de Barba',
            description='Hidratação diária',
            price=money('24.90'),
            category='barba',
            company_id=COMPANY_ID,
            status=True,
            url_image='https://placehold.co/600x400/png',
        ),
    ]
    session.add_all(base_products)
    await session.flush()
    return base_products


async def ensure_subscription_plans(
    session, services: list[Service]
) -> list[SubscriptionPlan]:
    q = select(SubscriptionPlan).where(
        SubscriptionPlan.company_id == COMPANY_ID,
        SubscriptionPlan.is_deleted.is_(False),
    )
    r = await session.execute(q)
    found = list(r.scalars().all())
    if found:
        return found

    if not services:
        return []

    main_service = services[0]
    plans = [
        SubscriptionPlan(
            company_id=COMPANY_ID,
            description='Quatro atendimentos com serviço principal do catálogo.',
            name='Plano mensal 4 usos',
            price=money('120.00'),
            uses_per_month=4,
            is_active=True,
        ),
        SubscriptionPlan(
            company_id=COMPANY_ID,
            description='Cortes ilimitados no mês (mesmo serviço base do catálogo).',
            name='Plano mensal ilimitado',
            price=money('199.90'),
            uses_per_month=None,
            is_active=True,
        ),
    ]
    session.add_all(plans)
    await session.flush()
    for p in plans:
        await session.execute(
            insert(subscription_plan_service_table).values(
                subscription_plan_id=p.id,
                service_id=main_service.id,
            )
        )
    return plans


async def ensure_template_marketing(session) -> int:
    q = select(TemplateMarketingModel).where(
        TemplateMarketingModel.company_id == COMPANY_ID,
        TemplateMarketingModel.is_deleted.is_(False),
    )
    r = await session.execute(q)
    if r.scalars().first() is not None:
        return 0

    session.add(
        TemplateMarketingModel(
            name='Lembrete de retorno (seed)',
            description='Mensagem padrão de follow-up (ambiente de dev).',
            context_template={
                'greeting': 'Olá, {{nome}}!',
                'body': 'Que tal agendar o próximo corte? Estamos de volta.',
                'cta': 'Responder SIM para sugestões de horário.',
            },
            company_id=COMPANY_ID,
            is_active=True,
        )
    )
    await session.flush()
    return 1


async def ensure_market_paid(session) -> int:
    q = select(MarketPaid).where(
        MarketPaid.company_id == COMPANY_ID,
        MarketPaid.is_deleted.is_(False),
    )
    r = await session.execute(q)
    if r.scalars().first() is not None:
        return 0

    # Valores de sandbox / placeholder — não use em produção
    ph = 'seed-placeholder-not-real'
    session.add(
        MarketPaid(
            company_id=COMPANY_ID,
            public_key=f'{ph}-pk',
            access_token=f'{ph}-at',
            market_paid_acess_token=f'{ph}-mpat',
            client_id=f'{ph}-client',
            client_secret=f'{ph}-secret',
        )
    )
    await session.flush()
    return 1


async def get_or_create_users(session, fake: Faker) -> list[User]:
    query = select(User).where(
        User.company_id == COMPANY_ID,
        User.is_deleted.is_(False),
    )
    result = await session.execute(query)
    users = list(result.scalars().all())
    if len(users) >= TARGET_USERS:
        return users

    missing = TARGET_USERS - len(users)
    for index in range(missing):
        serial = len(users) + index + 1
        name = fake.name()[:200]
        email = f'cliente.seed.{serial:04d}@local.dev'
        phone = f'11{9 + serial % 2:1d}9{serial % 10}{serial:07d}'[:20]
        user = User(
            name=name,
            email=email,
            phone=phone,
            password=hash_password(SEED_DEV_PASSWORD),
            is_active=True,
            company_id=COMPANY_ID,
            recurring_plan='free_plan',
        )
        session.add(user)
        users.append(user)

    await session.flush()
    return users


async def ensure_user_subscriptions(
    session,
    users: list[User],
    plans: list[SubscriptionPlan],
) -> int:
    if not users or not plans:
        return 0
    plan = plans[0]
    created = 0
    for user in users[:6]:
        q = select(UserSubscription).where(
            UserSubscription.user_id == user.id,
            UserSubscription.subscription_plan_id == plan.id,
            UserSubscription.is_deleted.is_(False),
        )
        r = await session.execute(q)
        if r.scalars().first() is not None:
            continue
        started = datetime.now(timezone.utc) - timedelta(days=20)
        session.add(
            UserSubscription(
                user_id=user.id,
                subscription_plan_id=plan.id,
                company_id=COMPANY_ID,
                status=UserSubscriptionStatus.active,
                started_at=started,
                ended_at=None,
            )
        )
        created += 1
    if created:
        await session.flush()
    return created


async def seed_schedule_blocks(session, employees: list[Employee]) -> int:
    if not employees:
        return 0
    r = await session.execute(
        select(ScheduleBlock).where(
            ScheduleBlock.company_id == COMPANY_ID,
            ScheduleBlock.is_deleted.is_(False),
        )
    )
    if r.scalars().first() is not None:
        return 0
    today = date.today()
    n = 0
    for emp in employees[:2]:
        session.add(
            ScheduleBlock(
                start_date=today + timedelta(days=1),
                end_date=today + timedelta(days=1),
                start_time=time(12, 0),
                end_time=time(13, 0),
                employee_id=emp.id,
                is_block=True,
                company_id=COMPANY_ID,
            )
        )
        n += 1
    await session.flush()
    return n


async def seed_cash_register(session, employees: list[Employee]) -> tuple[int, int]:
    if not employees:
        return 0, 0
    opener = employees[0]
    now = datetime.now(timezone.utc)
    sessions: list[CashRegisterSession] = []
    for day_offset in (3, 1):
        opened = (now - timedelta(days=day_offset)).replace(
            hour=8, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
        )
        closed = opened + timedelta(hours=9)
        sessions.append(
            CashRegisterSession(
                company_id=COMPANY_ID,
                opened_by=opener.id,
                closed_by=opener.id,
                opened_at=opened,
                closed_at=closed,
                opening_balance=money('200.00'),
                closing_balance=money('540.00'),
                expected_balance=money('530.00'),
                opening_notes='Abertura seed',
                closing_notes='Fechamento seed',
            )
        )
    for s in sessions:
        session.add(s)
    await session.flush()

    if sessions:
        s0 = sessions[0]
        session.add(
            CashRegisterAdjustment(
                session_id=s0.id,
                company_id=COMPANY_ID,
                kind=CashMovementKind.supply,
                amount=money('50.00'),
                description='Suprimento de troco (seed)',
                created_by=opener.id,
            )
        )
    await session.flush()
    return len(sessions), 1 if sessions else 0


# --- Agendamentos / financeiro (volume) --------------------------------------


async def get_existing_employees(session) -> list[Employee]:
    employee_ids = [eid for eid, _ in EMPLOYEES]
    query = select(Employee).where(
        Employee.company_id == COMPANY_ID,
        Employee.is_deleted.is_(False),
        Employee.id.in_(employee_ids),
    )
    result = await session.execute(query)
    return list(result.scalars().all())


def generate_schedule_times(
    base_day: datetime, duration_min: int
) -> tuple[datetime, datetime]:
    start_hour = random.choice([9, 10, 11, 13, 14, 15, 16, 17, 18])
    start_minute = random.choice([0, 15, 30, 45])
    time_start = base_day.replace(
        hour=start_hour,
        minute=start_minute,
        second=0,
        microsecond=0,
    )
    time_end = time_start + timedelta(minutes=duration_min)
    return time_start, time_end


def build_schedule_finance(
    schedule: Schedule,
    employee: Employee,
    service: Service,
    product: Product | None,
    time_end: datetime,
) -> ScheduleFinance:
    amount_service = money(service.price)
    amount_product = money(product.price) if product is not None else None
    amount_discount = (
        money(random.choice([0, 0, 0, 5, 8, 10, 12]))
        if random.random() < DISCOUNT_USAGE_PROBABILITY
        else None
    )

    gross = amount_service + (amount_product or Decimal('0'))
    total = max(gross - (amount_discount or Decimal('0')), Decimal('0'))

    payment_status = (
        PaymentStatus.paid
        if random.random() < PAYMENT_PAID_PROBABILITY
        else PaymentStatus.pending
    )
    # paid_at: naive datetime, alinhado ao restante do módulo
    paid_at = None
    if payment_status == PaymentStatus.paid:
        paid_at = time_end + timedelta(minutes=random.randint(5, 60))
        if paid_at.tzinfo is not None:
            paid_at = paid_at.replace(tzinfo=None)

    return ScheduleFinance(
        schedule_id=schedule.id,
        service_id=list(schedule.service_id),
        company_id=COMPANY_ID,
        created_by=employee.id,
        amount_service=amount_service,
        amount_product=amount_product,
        amount_discount=amount_discount,
        amount_total=money(total),
        payment_method=random.choice([
            PaymentMethod.pix,
            PaymentMethod.credit_card,
            PaymentMethod.debit_card,
            PaymentMethod.money,
        ]),
        payment_status=payment_status,
        paid_at=paid_at,
    )


async def seed_schedules_and_finances(
    session,
    employees: list[Employee],
    services: list[Service],
    products: list[Product],
    users: list[User],
    start_window: datetime,
) -> tuple[int, int]:
    created_schedules = 0
    created_finances = 0

    for employee in employees:
        employee_users = random.sample(users, k=min(MAX_USERS_PER_EMPLOYEE, len(users)))
        for _ in range(TARGET_SCHEDULES_PER_EMPLOYEE):
            day_offset = random.randint(0, METRICS_DAYS_WINDOW - 1)
            base_day = start_window + timedelta(days=day_offset)

            service = random.choice(services)
            user = random.choice(employee_users)
            use_product = bool(products) and (
                random.random() < PRODUCT_USAGE_PROBABILITY
            )
            product = random.choice(products) if use_product else None

            time_start, time_end = generate_schedule_times(
                base_day=base_day, duration_min=service.duration
            )
            time_register = time_start - timedelta(days=random.randint(1, 14))

            schedule = Schedule(
                user_id=user.id,
                service_id=[service.id],
                product_id=product.id if product is not None else None,
                employee_id=employee.id,
                company_id=COMPANY_ID,
                time_register=time_register,
                time_start=time_start,
                time_end=time_end,
                is_confirmed=True,
                is_canceled=False,
            )
            session.add(schedule)
            await session.flush()
            created_schedules += 1

            session.add(
                build_schedule_finance(
                    schedule=schedule,
                    employee=employee,
                    service=service,
                    product=product,
                    time_end=time_end,
                )
            )
            created_finances += 1

    return created_schedules, created_finances


def seed_expenses(session, employees: list[Employee], start_window: datetime) -> int:
    created_expenses = 0
    for index in range(TARGET_EXPENSES):
        employee = random.choice(employees)
        day_offset = random.randint(0, METRICS_DAYS_WINDOW - 1)
        occurred_at = start_window + timedelta(days=day_offset, hours=8)
        expense = Expense(
            company_id=COMPANY_ID,
            employee_id=random.choice([employee.id, None]),
            created_by=employee.id,
            description=f'SEED despesa {index + 1:02d}',
            amount=money(random.choice([30, 45, 60, 80, 120, 180, 250])),
            occurred_at=occurred_at,
        )
        session.add(expense)
        created_expenses += 1
    return created_expenses


# --- Orquestração -------------------------------------------------------------


async def run_bootstrap(session, fake: Faker) -> dict:
    await ensure_owner_and_company(session)
    await ensure_branch(session)
    employees = await ensure_catalog_employees(session)
    prof_cnt = await ensure_profiles(session, employees)
    services = await get_or_create_services(session)
    products = await get_or_create_products(session)
    plans = await ensure_subscription_plans(session, services)
    tmpl = await ensure_template_marketing(session)
    mp = await ensure_market_paid(session)
    users = await get_or_create_users(session, fake)
    sub = await ensure_user_subscriptions(session, users, plans)
    blocks = await seed_schedule_blocks(session, employees)
    cash_s, cash_adj = await seed_cash_register(session, employees)
    return {
        'profiles_created': prof_cnt,
        'services': len(services),
        'products': len(products),
        'subscription_plans': len(plans),
        'template_marketing': tmpl,
        'market_paid': mp,
        'users': len(users),
        'user_subscriptions': sub,
        'schedule_blocks': blocks,
        'cash_sessions': cash_s,
        'cash_adjustments': cash_adj,
    }


async def run_metrics(session, fake: Faker, start: datetime) -> dict:
    employees = await get_existing_employees(session)
    if not employees:
        msg = (
            'Nenhum colaborador do catálogo seed foi encontrado na company. '
            'Rode com --mode full ou --mode bootstrap antes.'
        )
        raise RuntimeError(msg)

    services = await get_or_create_services(session)
    products = await get_or_create_products(session)
    users = await get_or_create_users(session, fake)

    created_schedules, created_finances = await seed_schedules_and_finances(
        session=session,
        employees=employees,
        services=services,
        products=products,
        users=users,
        start_window=start,
    )
    created_expenses = seed_expenses(
        session=session,
        employees=employees,
        start_window=start,
    )
    return {
        'created_schedules': created_schedules,
        'created_finances': created_finances,
        'created_expenses': created_expenses,
    }


def parse_args() -> SeedMode:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        '--mode',
        choices=[m.value for m in SeedMode],
        default=SeedMode.full.value,
        help=('full: bootstrap + volume; bootstrap: entidades; metrics: agend./fin.'),
    )
    a = p.parse_args()
    return SeedMode(a.mode)


async def run() -> int:
    mode = parse_args()
    fake = build_faker()
    load_all_models()
    session_factory = get_session_factory()
    # Janela de "últimos 60 dias" (naive) — compatível com colunas do schema atual
    start_window = (
        datetime.now(timezone.utc) - timedelta(days=METRICS_DAYS_WINDOW)
    ).replace(tzinfo=None)

    async with session_factory() as session:
        summary: dict = {'mode': mode}
        if mode in (SeedMode.full, SeedMode.bootstrap):
            summary['bootstrap'] = await run_bootstrap(session, fake)
        if mode in (SeedMode.full, SeedMode.metrics):
            summary['metrics'] = await run_metrics(session, fake, start_window)
        await session.commit()

    print('--- Seed concluído ---')
    print(f'company_id: {COMPANY_ID}')
    print(f'mode: {mode.value}')
    for key, value in summary.items():
        if key == 'mode':
            continue
        print(f'{key}: {value}')
    pwd = SEED_DEV_PASSWORD
    print(f'\nUsuário seed: senha comum = {pwd!r} (clientes, staff, owner).')

    return 0


def main() -> None:
    raise SystemExit(asyncio.run(run()))


if __name__ == '__main__':
    main()
