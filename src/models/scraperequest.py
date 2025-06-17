from sqlalchemy import Column, Date, Integer, String, DateTime
from datetime import date, datetime

from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class ScrapeRequest(Base):
    __tablename__ = "scrape_requests"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_name_searched: Mapped[str] = mapped_column(String)
    requested_at: Mapped[date] = mapped_column(Date, default=date.today())
