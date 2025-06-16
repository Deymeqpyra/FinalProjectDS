from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import date, datetime

from sqlalchemy import JSON


class MarketplaceBase(BaseModel):
    name: str
    base_search_url: str
    product_selector: str
    title_selector: str
    price_selector: str
    link_selector: str
    description_selector: str


class MarketplaceCreate(MarketplaceBase):
    pass


class MarketplaceUpdate(MarketplaceBase):
    is_active: Optional[bool] = True


class MarketplaceOut(MarketplaceBase):
    id: int
    is_active: bool
    created_at: date
    updated_at: date

    class Config:
        orm_mode = True


class ScrapedProductBase(BaseModel):
    scraped_product_title: Optional[str] = None
    scraped_price: Optional[str] = None
    scraped_currency: Optional[str] = None
    scraped_description: Optional[dict] = None
    product_url: Optional[HttpUrl] = None
    scraped_at: date
    status: str
    error_message: Optional[str] = None
    marketplace_name: str


class ScrapedProductCreate(ScrapedProductBase):
    request_id: int
    marketplace_id: int


class ScrapedProductResponse(ScrapedProductBase):
    class Config:
        orm_mode = True


class ScrapeRequestBase(BaseModel):
    product_name_searched: str


class ScrapeRequestCreate(ScrapeRequestBase):
    pass


class ScrapeRequestResponse(ScrapeRequestBase):
    id: int
    requested_at: date

    class Config:
        orm_mode = True


class ScrapeResultItem(BaseModel):
    marketplace_name: str
    status: str
    product_title: Optional[str] = None
    price: Optional[str] = None
    description: Optional[dict] = None
    url: Optional[HttpUrl] = None
    scraped_at: date
    error_message: Optional[str] = None


class ScrapeProductResponse(BaseModel):
    scrape_request_id: int
    product_name_searched: str
    results: List[ScrapeResultItem]
    summary: dict
    scraped_at: date
