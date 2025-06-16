from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from database import Base


class ScrapedProduct(Base):
    __tablename__ = "scraped_products"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("scrape_requests.id"))
    marketplace_id = Column(Integer, ForeignKey("marketplaces.id"))
    scraped_product_title = Column(String)
    scraped_price = Column(String)
    scraped_currency = Column(String, nullable=True)
    product_url = Column(String)
    scraped_at = Column(DateTime, default=datetime.now())
    status = Column(String)
    error_message = Column(String, nullable=True)
