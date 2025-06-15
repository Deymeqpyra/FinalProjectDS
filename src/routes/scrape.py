from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import (
    ScrapeRequestCreate,
    ScrapeProductResponse,
    ScrapeResultItem,
    ScrapedProductCreate,
)
from crud import scrape as crud_scrape
from crud import marketplace as crud_marketplace
from service import scrape
from datetime import datetime
from typing import List, Optional

router = APIRouter()


@router.post("/", response_model=ScrapeProductResponse)
async def scrape_product_endpoint(
    request: ScrapeRequestCreate,
    db: AsyncSession = Depends(get_db),
    marketplace_ids: Optional[List[int]] = Query(
        default=None, description="Список id маркетплейсів для скрейпінгу"
    ),
):
    new_request = await crud_scrape.create_scrape_request(db, request)

    if marketplace_ids:
        marketplaces = []
        for mp_id in marketplace_ids:
            marketplace = await crud_marketplace.get_marketplace(db, mp_id)
            if marketplace:
                marketplaces.append(marketplace)
    else:
        marketplaces = await crud_marketplace.get_marketplaces(db)

    if not marketplaces:
        raise HTTPException(status_code=404, detail="Маркетплейси не знайдені")

    results = []

    for marketplace in marketplaces:
        scrape_result = await scrape.scrape_product(
            marketplace, request.product_name_searched
        )

        product_data = ScrapedProductCreate(
            request_id=new_request.id,
            marketplace_id=marketplace.id,
            scraped_product_title=scrape_result.get("product_title"),
            scraped_price=scrape_result.get("price"),
            scraped_currency=scrape_result.get("currency"),
            product_url=scrape_result.get("url"),
            scraped_at=scrape_result["scraped_at"],
            status=scrape_result["status"],
            error_message=scrape_result.get("error_message"),
            marketplace_name=marketplace.name,
        )

        await crud_scrape.save_scraped_product(db, product_data)

        results.append(
            ScrapeResultItem(
                marketplace_name=marketplace.name,
                status=scrape_result["status"],
                product_title=scrape_result.get("product_title"),
                price=scrape_result.get("price"),
                url=scrape_result.get("url"),
                scraped_at=scrape_result["scraped_at"],
                error_message=scrape_result.get("error_message"),
            )
        )

    return ScrapeProductResponse(
        scrape_request_id=new_request.id,
        product_name_searched=request.product_name_searched,
        results=results,
        summary={
            "total_marketplaces_processed": len(results),
            "successful_scrapes": sum(1 for r in results if r.status == "success"),
            "failed_scrapes": sum(1 for r in results if r.status != "success"),
        },
        scraped_at=datetime.utcnow(),
    )
