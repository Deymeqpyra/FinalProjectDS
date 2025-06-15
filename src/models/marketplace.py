from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database import Base


class Marketplace(Base):
    __tablename__ = "marketplaces"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    base_search_url = Column(String)
    product_selector = Column(String)
    title_selector = Column(String)
    price_selector = Column(String)
    link_selector = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())
