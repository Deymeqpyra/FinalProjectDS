from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.schemas import (
    ScrapeRequestCreate,
    ScrapeProductResponse,
    ScrapeResultItem,
    ScrapedProductCreate,
)
from src.crud import scrape as crud_scrape
from src.crud import marketplace as crud_marketplace
from src.crud import product as crud_product
from src.service import scrape
from src.models import scrapedproduct
from datetime import date, datetime
from typing import List, Optional, Dict, Any
import csv
import io
import re

router = APIRouter()


@router.get("/get-all-requests")
async def get_all(db: AsyncSession = Depends(get_db)):
    try:
        result = await crud_scrape.get_all_scrape_requests(db)
        if result is None:
            raise HTTPException(404, "Not found any writes")
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/get-request")
async def get_request(id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await crud_scrape.get_scrape_request(db, id)
        if result is None:
            raise HTTPException(404, "Not found")
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/get-request-by-date")
async def get_requests_by_date(date: date, db: AsyncSession = Depends(get_db)):
    try:
        result = await crud_scrape.get_requests_by_date(date, db)
        if result is None:
            raise HTTPException(404, "Not found")

        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/get-products-by-request-id")
async def get_products_by_request_id(id: int, db: AsyncSession = Depends(get_db)):
    try:
        request = await crud_scrape.get_scrape_request(db, id)
        if request is None:
            raise HTTPException(404, "Request not found")
        result = await crud_scrape.get_scraped_products_by_request_id(db, id)
        if result is None:
            raise HTTPException(404, "Not found any products by this request")
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/", response_model=ScrapeProductResponse)
async def scrape_by_query_name(
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
            product_id=None,
            scraped_product_title=scrape_result.get("product_title"),
            scraped_price=scrape_result.get("price"),
            scraped_currency=scrape_result.get("currency"),
            scraped_description=scrape_result.get("description"),

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

                description=scrape_result.get("description"),
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
        scraped_at=date.today(),
    )


@router.post("/get-by-product-id", response_model=ScrapeProductResponse)
async def scrape_product_endpoint(
    db: AsyncSession = Depends(get_db),
    marketplace_ids: Optional[List[int]] = Query(
        default=None, description="Список id маркетплейсів для скрейпінгу"
    ),
    product_id: int = Query(default=None, description="Продукт"),
):
    product = await crud_product.get_product(db, product_id)
    if product is None:
        raise HTTPException(404, "Product not found")
    request = ScrapeRequestCreate(product_name_searched=product.global_query_name)
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
            product_id=product.id,
            scraped_product_title=scrape_result.get("product_title"),
            scraped_price=scrape_result.get("price"),
            scraped_currency=scrape_result.get("currency"),
            scraped_description=scrape_result.get("description"),
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
                description=scrape_result.get("description"),
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
        scraped_at=date.today(),
    )
