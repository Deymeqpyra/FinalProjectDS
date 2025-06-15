from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from models.marketplace import Marketplace
from schemas import MarketplaceCreate, MarketplaceUpdate


async def create_marketplace(db: AsyncSession, marketplace: MarketplaceCreate):
    new_marketplace = Marketplace(**marketplace.model_dump())
    db.add(new_marketplace)
    await db.commit()
    await db.refresh(new_marketplace)
    return new_marketplace


async def get_marketplace(db: AsyncSession, marketplace_id: int):
    result = await db.execute(
        select(Marketplace).where(Marketplace.id == marketplace_id)
    )
    return result.scalar_one_or_none()


async def get_marketplaces(db: AsyncSession):
    result = await db.execute(select(Marketplace))
    return result.scalars().all()


async def update_marketplace(
    db: AsyncSession, marketplace_id: int, marketplace: MarketplaceUpdate
):
    await db.execute(
        update(Marketplace)
        .where(Marketplace.id == marketplace_id)
        .values(**marketplace.model_dump())
    )
    await db.commit()
    return await get_marketplace(db, marketplace_id)


async def delete_marketplace(db: AsyncSession, marketplace_id: int):
    await db.execute(delete(Marketplace).where(Marketplace.id == marketplace_id))
    await db.commit()
