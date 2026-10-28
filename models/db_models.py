from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from config.database import Base


class Manga(Base):
    __tablename__ = "manga"

    id = Column(Integer, primary_key=True, index=True)
    mal_id = Column(Integer, nullable=False, unique=True, index=True)
    title = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    stock_actual = Column(Integer, nullable=False, default=0)
    cost = Column(Numeric(10, 2), nullable=False)
    price_b2b = Column(Numeric(10, 2), nullable=False)
    lead_time_days = Column(Integer, nullable=False)
    demanda_diaria_promedio = Column(Float, nullable=False, default=0.0)

    orders = relationship(
        "B2BOrder",
        back_populates="manga",
        cascade="all, delete-orphan",
    )


class B2BOrder(Base):
    __tablename__ = "b2b_orders"

    id = Column(Integer, primary_key=True, index=True)
    manga_id = Column(Integer, ForeignKey("manga.id", ondelete="CASCADE"), nullable=False)
    client_name = Column(String, nullable=False)
    quantity_requested = Column(Integer, nullable=False)
    quantity_delivered = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    manga = relationship("Manga", back_populates="orders")