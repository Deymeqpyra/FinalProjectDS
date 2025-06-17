import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert
from sqlalchemy.orm import joinedload
from src.models import scraperequest
from src.models import scrapedproduct
from src.schemas import ScrapeRequestCreate
from src.schemas import ScrapedProductCreate


async def create_scrape_request(db: AsyncSession, request_data: ScrapeRequestCreate):
    new_request = scraperequest.ScrapeRequest(**request_data.dict())
    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)
    return new_request


async def get_scrape_request(db: AsyncSession, request_id: int):
    result = await db.execute(
        select(scraperequest.ScrapeRequest).where(
            scraperequest.ScrapeRequest.id == request_id
        )
    )
    return result.scalar_one_or_none()


async def get_all_scrape_requests(db: AsyncSession):
    result = await db.execute(select(scraperequest.ScrapeRequest))
    return result.scalars().all()


async def get_requests_by_date(date: datetime.date, db: AsyncSession):
    result = await db.execute(
        select(scraperequest.ScrapeRequest).where(
            scraperequest.ScrapeRequest.requested_at == date
        )
    )
    return result.scalars().all()


async def find_product_by_marketplace(
    product_id: int, marketplace_id: int, db: AsyncSession
):
    result = await db.execute(
        select(scrapedproduct.ScrapedProduct)
        .where(scrapedproduct.ScrapedProduct.marketplace_id == marketplace_id)
        .where(scrapedproduct.ScrapedProduct.product_id == product_id)
    )
    return result.scalars().one()


async def save_scraped_product(db: AsyncSession, product_data: ScrapedProductCreate):
    new_product = scrapedproduct.ScrapedProduct(
        request_id=product_data.request_id,
        marketplace_id=product_data.marketplace_id,
        product_id=product_data.product_id,
        scraped_product_title=product_data.scraped_product_title,
        scraped_price=product_data.scraped_price,
        scraped_currency=product_data.scraped_currency,
        product_url=str(product_data.product_url),
        scraped_at=product_data.scraped_at,
        status=product_data.status,
        scraped_description=product_data.scraped_description,
        error_message=product_data.error_message,
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product


async def get_scraped_products_by_request_id(db: AsyncSession, request_id: int):
    result = await db.execute(
        select(scrapedproduct.ScrapedProduct).where(
            scrapedproduct.ScrapedProduct.request_id == request_id
        )
    )
    return result.scalars().all()
