"""
/home/marcus/code/marcus/robo-advisor/app/schemas/financial_modeling.py
Pydantic schemas for financial modeling validation.
This file defines the data structures for financial analysis requests and responses.
RELEVANT FILES: app/routes.py, app/services/financial_modeling_service.py
"""

from pydantic import BaseModel
from datetime import date


class FinancialModelingRequest(BaseModel):
    """Request schema for financial metrics calculation."""
    tickers: list[str]
    start_date: date
    end_date: date


class FinancialModelingResponse(BaseModel):
    """Response schema for financial metrics."""
    expected_returns: dict[str, float]
    covariance_matrix: dict[str, dict[str, float]]


class PortfolioAnalysisRequest(BaseModel):
    """Request schema for portfolio analysis."""
    risk_free_rate: float


class PortfolioAnalysisResponse(BaseModel):
    """Response schema for portfolio analysis results."""
    sharpe_ratio: float
    tangency_portfolio_weights: dict[str, float]
    markowitz_bullet_plot: str
