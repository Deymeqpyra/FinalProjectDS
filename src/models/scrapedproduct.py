from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from database import Base


class ScrapedProduct(Base):
    __tablename__ = "scraped_products"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("scrape_requests.id"))
    marketplace_id: Mapped[int] = mapped_column(ForeignKey("marketplaces.id"))
    scraped_product_title: Mapped[str] = mapped_column(String)
    scraped_price: Mapped[str] = mapped_column(String)
    scraped_currency: Mapped[str | None] = mapped_column(String, nullable=True)
    scraped_description: Mapped[str | None] = mapped_column(String, nullable=True)
    product_url: Mapped[str] = mapped_column(String)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    status: Mapped[str] = mapped_column(String)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
