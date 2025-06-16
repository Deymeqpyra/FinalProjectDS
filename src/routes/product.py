from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud import product as crud_product
from schemas import (
    ProductCreate,
    ProductUpdate,
)

router = APIRouter()


@router.post("/create-product")
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await crud_product.create_product(db, product)


@router.get("/get-products")
async def read_product(db: AsyncSession = Depends(get_db)):
    return await crud_product.get_products(db)


@router.get("/get-product")
async def read_marketplace(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await crud_product.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


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
