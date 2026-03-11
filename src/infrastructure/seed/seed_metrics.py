import asyncio
import random
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy import select

from src.infrastructure.database import load_all_models
from src.infrastructure.database.models.commom.payment_method import PaymentMethod
from src.infrastructure.database.models.commom.payment_status import PaymentStatus
from src.infrastructure.database.models.employees import Employee
from src.infrastructure.database.models.expense import Expense
from src.infrastructure.database.models.product import Product
from src.infrastructure.database.models.schedule import Schedule
from src.infrastructure.database.models.schedule_finance import ScheduleFinance
from src.infrastructure.database.models.service import Service
from src.infrastructure.database.models.users import User
from src.infrastructure.database.session import get_session_factory

COMPANY_ID = UUID('129d8d2d-0828-47a9-b586-8088c33eae8f')
EMPLOYEES = [
    (UUID('8670fbed-63ca-4046-aaf8-6eb48dcf180e'), 'Hedris'),
    (UUID('cdc28bc7-3cb8-423e-86f2-689591726adb'), 'Henrique'),
    (UUID('98de56cf-7197-49b3-a63c-ede4def98872'), 'Todas'),
    (UUID('d54667fb-82f3-479a-9324-aae32b6d7ae9'), 'Fabin'),
    (UUID('89a46fed-d9fc-4dd8-bea6-f20aa9dff25f'), 'Nilson'),
]

RANDOM_SEED = 20260311
METRICS_DAYS_WINDOW = 60
TARGET_SCHEDULES_PER_EMPLOYEE = 28
TARGET_EXPENSES = 22
TARGET_USERS = 35
MAX_USERS_PER_EMPLOYEE = 18
PRODUCT_USAGE_PROBABILITY = 0.45
DISCOUNT_USAGE_PROBABILITY = 0.28
PAYMENT_PAID_PROBABILITY = 0.90


def money(value: Decimal | float | int) -> Decimal:
    return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


async def get_existing_employees(session) -> list[Employee]:
    employee_ids = [employee_id for employee_id, _ in EMPLOYEES]
    query = select(Employee).where(
        Employee.company_id.__eq__(COMPANY_ID),
        Employee.is_deleted.__eq__(False),
        Employee.id.in_(employee_ids),
    )
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_or_create_services(session) -> list[Service]:
    query = select(Service).where(
        Service.company_id.__eq__(COMPANY_ID),
        Service.is_deleted.__eq__(False),
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
        Product.company_id.__eq__(COMPANY_ID),
        Product.is_deleted.__eq__(False),
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


async def get_or_create_users(session) -> list[User]:
    query = select(User).where(
        User.company_id.__eq__(COMPANY_ID),
        User.is_deleted.__eq__(False),
    )
    result = await session.execute(query)
    users = list(result.scalars().all())
    if len(users) >= TARGET_USERS:
        return users

    missing = TARGET_USERS - len(users)
    for index in range(missing):
        serial = len(users) + index + 1
        user = User(
            name=f'Cliente {serial:03d}',
            email=f'cliente{serial:03d}@seed.local',
            phone=f'1199000{serial:04d}',
            password='seed_password_hash',
            is_active=True,
            company_id=COMPANY_ID,
            recurring_plan='free_plan',
        )
        session.add(user)
        users.append(user)

    await session.flush()
    return users


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
    paid_at = (
        time_end + timedelta(minutes=random.randint(5, 60))
        if payment_status == PaymentStatus.paid
        else None
    )

    return ScheduleFinance(
        schedule_id=schedule.id,
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
                service_id=service.id,
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
            description=f'SEED_METRICS despesa {index + 1:02d}',
            amount=money(random.choice([30, 45, 60, 80, 120, 180, 250])),
            occurred_at=occurred_at,
        )
        session.add(expense)
        created_expenses += 1
    return created_expenses


async def seed_schedules_finance_and_expenses() -> None:
    random.seed(RANDOM_SEED)
    session_factory = get_session_factory()

    async with session_factory() as session:
        employees = await get_existing_employees(session)
        if not employees:
            raise RuntimeError(
                'Nenhum employee informado foi encontrado no banco para a company.'
            )

        services = await get_or_create_services(session)
        products = await get_or_create_products(session)
        users = await get_or_create_users(session)

        start_window = datetime.now() - timedelta(days=METRICS_DAYS_WINDOW)

        created_schedules, created_finances = await seed_schedules_and_finances(
            session=session,
            employees=employees,
            services=services,
            products=products,
            users=users,
            start_window=start_window,
        )
        created_expenses = seed_expenses(
            session=session,
            employees=employees,
            start_window=start_window,
        )
        await session.commit()

    print('Seed de métricas concluído com sucesso.')
    print(f'company_id: {COMPANY_ID}')
    print(f'funcionários encontrados: {len(employees)}')
    print(f'schedules criados: {created_schedules}')
    print(f'schedule_finance criados: {created_finances}')
    print(f'expenses criadas: {created_expenses}')


def main() -> None:
    load_all_models()
    asyncio.run(seed_schedules_finance_and_expenses())


if __name__ == '__main__':
    main()
