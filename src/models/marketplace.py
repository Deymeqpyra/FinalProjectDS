from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from database import Base


class Marketplace(Base):
    __tablename__ = "marketplaces"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    base_search_url: Mapped[str] = mapped_column(String)
    product_selector: Mapped[str] = mapped_column(String)
    tag: Mapped[str] = mapped_column(String, nullable=True)
    additional_tag: Mapped[str] = mapped_column(String, nullable=True)
    title_selector: Mapped[str] = mapped_column(String)
    price_selector: Mapped[str] = mapped_column(String)
    link_selector: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
