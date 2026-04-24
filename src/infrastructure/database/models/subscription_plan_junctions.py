from sqlalchemy import Column, ForeignKey, Integer, Table, Uuid

from src.infrastructure.database.models.base import BaseModel

subscription_plan_service_table = Table(
    'subscription_plan_service',
    BaseModel.metadata,
    Column(
        'subscription_plan_id',
        Uuid,
        ForeignKey('subscription_plan.id', ondelete='CASCADE'),
        primary_key=True,
    ),
    Column('service_id', Uuid, ForeignKey('service.id'), primary_key=True),
)

subscription_plan_product_table = Table(
    'subscription_plan_product',
    BaseModel.metadata,
    Column(
        'subscription_plan_id',
        Uuid,
        ForeignKey('subscription_plan.id', ondelete='CASCADE'),
        primary_key=True,
    ),
    Column('product_id', Uuid, ForeignKey('product.id'), primary_key=True),
    Column('quantity', Integer, nullable=False, server_default='1'),
)
