from sqlalchemy import JSON, Date, String, Boolean, DateTime, null
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime
from src.database import Base


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(index=True, primary_key=True)
    global_query_name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
