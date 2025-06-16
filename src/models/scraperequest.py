from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base


class ScrapeRequest(Base):
    __tablename__ = "scrape_requests"
    id = Column(Integer, primary_key=True, index=True)
    product_name_searched = Column(String)
    requested_at = Column(DateTime, default=datetime.now())
