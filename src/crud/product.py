from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from src.models.product import Product
from src.schemas import ProductCreate, ProductUpdate


async def create_product(db: AsyncSession, product: ProductCreate):
    new_product = Product(**product.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product


async def get_product(db: AsyncSession, product_id: int):
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


async def get_products(db: AsyncSession):
    result = await db.execute(select(Product))
    return result.scalars().all()


async def update_product(db: AsyncSession, product: ProductUpdate):
    await db.execute(
        update(Product).where(Product.id == product.id).values(**product.model_dump())
    )
    await db.commit()
    return await get_product(db, product.id)


async def delete_product(db: AsyncSession, product_id: int):
    await db.execute(delete(Product).where(Product.id == product_id))
    await db.commit()
