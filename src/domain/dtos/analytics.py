from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class DashboardFilterDTO(BaseModel):
    company_id: UUID
    start_date: date
    end_date: date
    employee_id: Optional[UUID] = None


class MonthlySummaryDTO(BaseModel):
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
    atendimentos_por_dia: float


class BarberRankingItemDTO(BaseModel):
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


class CustomerMetricsDTO(BaseModel):
    clientes_distintos: int
    clientes_novos: int
    clientes_recorrentes: int
    frequencia_media: float
    clientes_nunca_voltaram: int
    taxa_retorno_percentual: float


class DashboardMetricsDTO(BaseModel):
    resumo_mes: MonthlySummaryDTO
    ranking_barbeiros: List[BarberRankingItemDTO]
    indicadores_clientes: CustomerMetricsDTO
