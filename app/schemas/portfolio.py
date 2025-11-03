"""Pydantic schemas for request/response validation."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PortfolioBase(BaseModel):
    """Base portfolio schema."""

    name: str
    description: Optional[str] = None


class PortfolioCreate(PortfolioBase):
    """Schema for creating a portfolio."""

    pass


class PortfolioUpdate(BaseModel):
    """Schema for updating a portfolio."""

    name: Optional[str] = None
    description: Optional[str] = None


class Portfolio(PortfolioBase):
    """Schema for portfolio response."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssetBase(BaseModel):
    """Base asset schema."""

    symbol: str
    name: str
    quantity: Decimal
    purchase_price: Optional[Decimal] = None


class AssetCreate(AssetBase):
    """Schema for creating an asset."""

    portfolio_id: int


class AssetUpdate(BaseModel):
    """Schema for updating an asset."""

    symbol: Optional[str] = None
    name: Optional[str] = None
    quantity: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None


class Asset(AssetBase):
    """Schema for asset response."""

    id: int
    portfolio_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
