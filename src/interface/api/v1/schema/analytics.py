from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class DashboardFilterInSchema(BaseModel):
    start_date: date
    end_date: date
    employee_id: Optional[UUID] = None

    @model_validator(mode='after')
    def validate_period(self) -> 'DashboardFilterInSchema':
        if self.end_date < self.start_date:
            raise ValueError('end_date deve ser maior ou igual a start_date')
        return self


class MonthlySummaryOutSchema(BaseModel):
    faturamento_bruto: Decimal
    despesas: Decimal
    lucro: Decimal
    margem_percentual: float
    total_atendimentos: int
    clientes_distintos: int
    ticket_medio_atendimento: Decimal
    ticket_medio_cliente: Decimal
    clientes_novos_periodo: int
    taxa_retorno_percentual: float
    atendimentos_por_dia: float = Field(
        description='Total de atendimentos dividido por dias trabalhados no período'
    )


class BarberRankingItemOutSchema(BaseModel):
    employee_id: UUID
    employee_name: str
    faturamento: Decimal
    atendimentos: int
    clientes_distintos: int
    ticket_medio_atendimento: Decimal
    ticket_medio_cliente: Decimal
    clientes_novos: int
    taxa_retorno_percentual: float
    frequencia_media_clientes: float


class CustomerMetricsOutSchema(BaseModel):
    clientes_distintos: int
    clientes_novos: int
    clientes_recorrentes: int
    frequencia_media: float
    clientes_nunca_voltaram: int
    taxa_retorno_percentual: float


class DashboardMetricsOutSchema(BaseModel):
    resumo_mes: MonthlySummaryOutSchema
    ranking_barbeiros: List[BarberRankingItemOutSchema]
    indicadores_clientes: CustomerMetricsOutSchema
