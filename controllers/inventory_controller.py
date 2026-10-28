from decimal import Decimal
from typing import Generator

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from config.database import SessionLocal
from models.db_models import B2BOrder, Manga
from models.schemas import (
    B2BOrderResponse,
    DashboardSummary,
    MangaCreate,
    MangaInventoryResponse,
)


router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class B2BOrderCreate(BaseModel):
    manga_id: int = Field(gt=0)
    client_name: str = Field(min_length=1)
    quantity_requested: int = Field(gt=0)
    quantity_delivered: int = Field(default=0, ge=0)


class DashboardResponse(BaseModel):
    mangas: list[MangaInventoryResponse]
    summary: DashboardSummary


@router.post("/manga", response_model=MangaInventoryResponse, status_code=status.HTTP_201_CREATED)
async def add_manga(
    manga_data: MangaCreate,
    db: Session = Depends(get_db),
) -> MangaInventoryResponse:
    data = manga_data.model_dump()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"https://api.jikan.moe/v4/manga/{manga_data.mal_id}"
            )
            response.raise_for_status()
            jikan_manga = response.json().get("data", {})
            data["title"] = jikan_manga.get("title") or data["title"]
            images = jikan_manga.get("images", {}).get("jpg", {})
            data["image_url"] = images.get("large_image_url") or images.get(
                "image_url"
            ) or data["image_url"]
    except (httpx.HTTPError, ValueError, TypeError, AttributeError):
        # Jikan is an enrichment source; submitted values remain valid fallbacks.
        pass

    data["demanda_diaria_promedio"] = float(data["demanda_diaria_promedio"])
    manga = Manga(**data)
    db.add(manga)
    try:
        db.commit()
        db.refresh(manga)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un manga con ese mal_id.",
        ) from exc

    return _inventory_response(manga, [])


@router.post("/order", response_model=B2BOrderResponse, status_code=status.HTTP_201_CREATED)
def register_order(
    order_data: B2BOrderCreate,
    db: Session = Depends(get_db),
) -> B2BOrder:
    manga = db.query(Manga).filter(Manga.id == order_data.manga_id).first()
    if manga is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe un manga con ese manga_id.",
        )
    if order_data.quantity_delivered > order_data.quantity_requested:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La cantidad entregada no puede superar la solicitada.",
        )

    if order_data.quantity_delivered == 0:
        order_status = "Pendiente"
    elif order_data.quantity_delivered < order_data.quantity_requested:
        order_status = "Parcial"
    else:
        order_status = "Completado"

    order = B2BOrder(
        manga_id=order_data.manga_id,
        client_name=order_data.client_name.strip(),
        quantity_requested=order_data.quantity_requested,
        quantity_delivered=order_data.quantity_delivered,
        status=order_status,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)) -> DashboardResponse:
    mangas = db.query(Manga).options(joinedload(Manga.orders)).all()
    inventory = [_inventory_response(manga, manga.orders) for manga in mangas]

    requested_total = sum(
        (order.quantity_requested for manga in mangas for order in manga.orders),
        0,
    )
    delivered_total = sum(
        (order.quantity_delivered for manga in mangas for order in manga.orders),
        0,
    )
    global_fill_rate = (
        Decimal(delivered_total) / Decimal(requested_total) * Decimal("100")
        if requested_total
        else Decimal("100.0")
    )

    summary = DashboardSummary(
        fill_rate_global=global_fill_rate,
        total_productos_obsoletos=sum(
            item.estado_movimiento == "Movimiento Lento" for item in inventory
        ),
        total_alertas_reorden=sum(
            item.estado_movimiento == "Stock Crítico" for item in inventory
        ),
    )
    return DashboardResponse(mangas=inventory, summary=summary)


def _inventory_response(manga: Manga, orders: list[B2BOrder]) -> MangaInventoryResponse:
    requested = sum(order.quantity_requested for order in orders)
    delivered = sum(order.quantity_delivered for order in orders)
    fill_rate = (
        Decimal(delivered) / Decimal(requested) * Decimal("100")
        if requested
        else Decimal("100.0")
    )

    demand = Decimal(str(manga.demanda_diaria_promedio))
    stock = Decimal(manga.stock_actual)
    lead_time = Decimal(manga.lead_time_days)
    dias_inventario = stock / demand if demand > 0 else Decimal("999.0")
    rotacion = (
        demand * Decimal("365") / stock if stock > 0 else Decimal("0.0")
    )
    safety_stock = int((demand * Decimal("1.5")) * lead_time)
    reorder_point = int(demand * lead_time) + safety_stock

    if manga.stock_actual <= reorder_point:
        estado_movimiento = "Stock Crítico"
    elif dias_inventario > Decimal("90"):
        estado_movimiento = "Movimiento Lento"
    else:
        estado_movimiento = "Óptimo"

    return MangaInventoryResponse(
        id=manga.id,
        mal_id=manga.mal_id,
        title=manga.title,
        image_url=manga.image_url,
        stock_actual=manga.stock_actual,
        cost=Decimal(str(manga.cost)),
        price_b2b=Decimal(str(manga.price_b2b)),
        lead_time_days=manga.lead_time_days,
        demanda_diaria_promedio=demand,
        rotacion_inventario=rotacion,
        dias_inventario=dias_inventario,
        fill_rate=fill_rate,
        safety_stock=safety_stock,
        reorder_point=reorder_point,
        estado_movimiento=estado_movimiento,
    )