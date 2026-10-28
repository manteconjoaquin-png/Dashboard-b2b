from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class MangaBase(BaseModel):
    mal_id: int = Field(gt=0)
    title: str = Field(min_length=1)
    image_url: str = Field(min_length=1)
    stock_actual: int = Field(default=0, ge=0)
    cost: Decimal = Field(ge=0)
    price_b2b: Decimal = Field(ge=0)
    lead_time_days: int = Field(ge=0)
    demanda_diaria_promedio: Decimal = Field(default=Decimal("0"), ge=0)

    @field_validator("cost", "price_b2b", "demanda_diaria_promedio")
    @classmethod
    def validate_finite_decimal(cls, value: Decimal) -> Decimal:
        if not value.is_finite():
            raise ValueError("El valor debe ser un decimal finito")
        return value

    class Config:
        from_attributes = True


class MangaCreate(MangaBase):
    class Config:
        from_attributes = True


class B2BOrderResponse(BaseModel):
    id: int
    manga_id: int
    client_name: str = Field(min_length=1)
    quantity_requested: int = Field(ge=0)
    quantity_delivered: int = Field(ge=0)
    status: str = Field(min_length=1)
    created_at: datetime

    class Config:
        from_attributes = True


class MangaInventoryResponse(MangaBase):
    id: int
    rotacion_inventario: Decimal = Field(ge=0)
    dias_inventario: Decimal = Field(ge=0)
    fill_rate: Decimal = Field(ge=0)
    safety_stock: int = Field(ge=0)
    reorder_point: int = Field(ge=0)
    estado_movimiento: str = Field(min_length=1)

    @field_validator("rotacion_inventario", "dias_inventario", "fill_rate")
    @classmethod
    def validate_finite_metrics(cls, value: Decimal) -> Decimal:
        if not value.is_finite():
            raise ValueError("La métrica debe ser un decimal finito")
        return value

    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    fill_rate_global: Decimal = Field(ge=0)
    total_productos_obsoletos: int = Field(ge=0)
    total_alertas_reorden: int = Field(ge=0)

    @field_validator("fill_rate_global")
    @classmethod
    def validate_finite_fill_rate(cls, value: Decimal) -> Decimal:
        if not value.is_finite():
            raise ValueError("El fill rate debe ser un decimal finito")
        return value

    class Config:
        from_attributes = True