from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.crud import marketplace as crud_marketplace
from src.schemas import MarketplaceCreate, MarketplaceUpdate, MarketplaceOut

router = APIRouter()


@router.post("/", response_model=MarketplaceOut)
async def create_marketplace(
    marketplace: MarketplaceCreate, db: AsyncSession = Depends(get_db)
):
    return await crud_marketplace.create_marketplace(db, marketplace)


@router.get("/", response_model=list[MarketplaceOut])
async def read_marketplaces(db: AsyncSession = Depends(get_db)):
    return await crud_marketplace.get_marketplaces(db)


@router.get("/{marketplace_id}", response_model=MarketplaceOut)
async def read_marketplace(marketplace_id: int, db: AsyncSession = Depends(get_db)):
    marketplace = await crud_marketplace.get_marketplace(db, marketplace_id)
    if marketplace is None:
        raise HTTPException(status_code=404, detail="Marketplace not found")
    return marketplace


@router.put("/{marketplace_id}", response_model=MarketplaceOut)
async def update_marketplace(
    marketplace_id: int,
    marketplace: MarketplaceUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await crud_marketplace.update_marketplace(db, marketplace_id, marketplace)


@router.delete("/{marketplace_id}")
async def delete_marketplace(marketplace_id: int, db: AsyncSession = Depends(get_db)):
    await crud_marketplace.delete_marketplace(db, marketplace_id)
    return {"detail": "Marketplace deleted"}
