import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.crud import product as crud_product
from src.crud import marketplace as crud_marketplace
from src.crud import scrape as crud_scrape
from src.schemas import (
    ProductCreate,
    ProductUpdate,
)

router = APIRouter()


@router.post("/create-product")
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await crud_product.create_product(db, product)


@router.get("/get-products")
async def read_products(db: AsyncSession = Depends(get_db)):
    return await crud_product.get_products(db)


@router.get("/get-product")
async def read_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await crud_product.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/compare")
async def compare_product_price(
    product_id: int,
    marketplace_id1: int,
    marketplace_id2: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        product = await crud_product.get_product(db, product_id)
        if product is None:
            raise HTTPException(404, "Product not found")
        marketplace1 = await crud_marketplace.get_marketplace(db, marketplace_id1)
        marketplace2 = await crud_marketplace.get_marketplace(db, marketplace_id2)
        if marketplace2 is None or marketplace1 is None:
            raise HTTPException(404, "Marketplace not found")
        scraped_product1 = await crud_scrape.find_product_by_marketplace(
            product.id, marketplace1.id, db
        )
        scraped_product2 = await crud_scrape.find_product_by_marketplace(
            product.id, marketplace2.id, db
        )
        price1 = re.sub(r"[^\d]", "", scraped_product1.scraped_price)
        value1 = int(price1)
        price2 = re.sub(r"[^\d]", "", scraped_product2.scraped_price)
        value2 = int(price2)
        if value2 > value1:
            return {
                "product": scraped_product2,
                "result": f"Marketplace {marketplace2.name} has the lowest price!",
            }
        if value1 > value2:
            return {
                "product": scraped_product2,
                "result": f"Marketplace {marketplace1.name} has the lowest price!",
            }
        if value1 == value2:
            return {
                "product": scraped_product2,
                "result": f"Marketplace {marketplace1.name} and {marketplace2.name} has the same price!",
            }

    except Exception as e:
        raise HTTPException(500, str(e))


@router.put("/update-product")
async def update_product(
    product: ProductUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await crud_product.update_product(db, product)


@router.delete("/delete-product")
async def delete_marketplace(product_id: int, db: AsyncSession = Depends(get_db)):
    await crud_product.delete_product(db, product_id)
    return {"detail": "Product deleted"}
