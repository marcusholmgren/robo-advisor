"""API routes for the robo-advisor application."""

from typing import List
from fastapi import APIRouter, HTTPException, status
from tortoise.exceptions import DoesNotExist

from app import schemas
from app.models import Portfolio, Asset

router = APIRouter()


# Portfolio endpoints
@router.get("/portfolios", response_model=List[schemas.Portfolio])
async def list_portfolios():
    """List all portfolios."""
    portfolios = await Portfolio.all()
    return portfolios


@router.get("/portfolios/{portfolio_id}", response_model=schemas.Portfolio)
async def get_portfolio(portfolio_id: int):
    """Get a specific portfolio by ID."""
    try:
        portfolio = await Portfolio.get(id=portfolio_id)
        return portfolio
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found"
        )


@router.post("/portfolios", response_model=schemas.Portfolio, status_code=status.HTTP_201_CREATED)
async def create_portfolio(portfolio: schemas.PortfolioCreate):
    """Create a new portfolio."""
    portfolio_obj = await Portfolio.create(**portfolio.model_dump())
    return portfolio_obj


@router.put("/portfolios/{portfolio_id}", response_model=schemas.Portfolio)
async def update_portfolio(portfolio_id: int, portfolio: schemas.PortfolioUpdate):
    """Update an existing portfolio."""
    try:
        portfolio_obj = await Portfolio.get(id=portfolio_id)
        update_data = portfolio.model_dump(exclude_unset=True)
        await portfolio_obj.update_from_dict(update_data).save()
        return portfolio_obj
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found"
        )


@router.delete("/portfolios/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(portfolio_id: int):
    """Delete a portfolio."""
    try:
        portfolio = await Portfolio.get(id=portfolio_id)
        await portfolio.delete()
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found"
        )


# Asset endpoints
@router.get("/assets", response_model=List[schemas.Asset])
async def list_assets(portfolio_id: int = None):
    """List all assets, optionally filtered by portfolio."""
    if portfolio_id:
        assets = await Asset.filter(portfolio_id=portfolio_id)
    else:
        assets = await Asset.all()
    return assets


@router.get("/assets/{asset_id}", response_model=schemas.Asset)
async def get_asset(asset_id: int):
    """Get a specific asset by ID."""
    try:
        asset = await Asset.get(id=asset_id)
        return asset
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found"
        )


@router.post("/assets", response_model=schemas.Asset, status_code=status.HTTP_201_CREATED)
async def create_asset(asset: schemas.AssetCreate):
    """Create a new asset."""
    # Check if portfolio exists
    try:
        await Portfolio.get(id=asset.portfolio_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {asset.portfolio_id} not found"
        )
    
    asset_data = asset.model_dump()
    asset_obj = await Asset.create(**asset_data)
    return asset_obj


@router.put("/assets/{asset_id}", response_model=schemas.Asset)
async def update_asset(asset_id: int, asset: schemas.AssetUpdate):
    """Update an existing asset."""
    try:
        asset_obj = await Asset.get(id=asset_id)
        update_data = asset.model_dump(exclude_unset=True)
        await asset_obj.update_from_dict(update_data).save()
        return asset_obj
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found"
        )


@router.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: int):
    """Delete an asset."""
    try:
        asset = await Asset.get(id=asset_id)
        await asset.delete()
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found"
        )
