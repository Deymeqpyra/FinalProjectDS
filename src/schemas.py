from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict
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
    product_id: Optional[int] = None


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


class ProductBase(BaseModel):
    global_query_name: str
    description: str


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    id: int


class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True

#regression
class RegressionConfig(BaseModel):
    dependent_variable: str = Field(..., description="Назва залежної змінної (Y)")
    independent_variables: List[str] = Field(..., description="Список незалежних змінних (X)")

class ModelSummary(BaseModel):
    coefficients: Dict[str, float]
    std_errors: Dict[str, float]
    t_statistics: Dict[str, float]
    p_values: Dict[str, float]
    confidence_intervals: Dict[str, List[float]]

class ModelQuality(BaseModel):
    r_squared: float
    adj_r_squared: float
    f_statistic: float
    f_p_value: float
    n_observations: int

class RegressionResponse(BaseModel):
    analysis_id: int
    model_summary: ModelSummary
    model_quality: ModelQuality
    formula: str