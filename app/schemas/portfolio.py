"""Pydantic schemas for request/response validation."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
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
    """Base asset schema, without quantity or price."""

    symbol: str
    name: str


class AssetCreate(AssetBase):
    """Schema for creating an asset."""

    portfolio_id: int


class AssetUpdate(BaseModel):
    """Schema for updating an asset (e.g., renaming)."""

    symbol: Optional[str] = None
    name: Optional[str] = None


class Asset(AssetBase):
    """
    Schema for asset response. Includes calculated fields for current state.
    """

    id: int
    portfolio_id: int
    created_at: datetime
    updated_at: datetime

    # Optional fields that can be populated by API endpoints
    current_quantity: Optional[float] = None
    average_cost_basis: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


# --- New Schemas for Trades ---


class TradeBase(BaseModel):
    """Base schema for a trade."""

    trade_date: datetime
    quantity: Decimal
    price: Decimal
    trade_type: str = "BUY"

    model_config = ConfigDict(json_encoders={Decimal: str})


class TradeCreate(TradeBase):
    """Schema for creating a new trade for an asset."""

    asset_id: int


class Trade(TradeBase):
    """Schema for trade response."""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssetHolding(Asset):
    """Schema for asset response, including holdings and weight."""

    holdings: float
    weight: float


class PortfolioDetails(Portfolio):
    """Schema for portfolio response, including asset holdings."""

    assets: List[AssetHolding]
