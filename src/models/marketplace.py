from sqlalchemy import JSON, Date, String, Boolean, DateTime, null
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime
from src.database import Base


class Marketplace(Base):
    __tablename__ = "marketplaces"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    base_search_url: Mapped[str] = mapped_column(String, nullable=True)
    product_selector: Mapped[str] = mapped_column(String, nullable=True)
    tag: Mapped[str] = mapped_column(String, nullable=True)
    additional_tag: Mapped[str] = mapped_column(String, nullable=True)
    title_selector: Mapped[str] = mapped_column(String, nullable=True)
    price_selector: Mapped[str] = mapped_column(String, nullable=True)
    link_selector: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    description_selector: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[date] = mapped_column(Date, default=date.today())
    updated_at: Mapped[date] = mapped_column(Date, default=date.today())
