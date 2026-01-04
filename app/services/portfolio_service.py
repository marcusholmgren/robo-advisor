"""
/home/marcus/code/marcus/robo-advisor/app/services/portfolio_service.py
Service for portfolio-related operations.
This file handles complex portfolio logic, including calculating holdings and weights.
RELEVANT FILES: app/models.py, app/routes.py, app/schemas/portfolio.py
"""

import yfinance as yf
from tortoise.exceptions import DoesNotExist
from app.models import Portfolio


class PortfolioService:
    """Service for portfolio-related operations."""

    async def get_portfolio_details(self, portfolio_id: int):
        """
        Get a portfolio with its assets, including holdings and weights.

        Args:
            portfolio_id: The ID of the portfolio to retrieve.

        Returns:
            A dictionary containing the portfolio details, or None if not found.
        """
        try:
            portfolio = await Portfolio.get(id=portfolio_id).prefetch_related(
                "assets", "assets__trades"
            )
        except DoesNotExist:
            return None

        total_holdings_value = 0
        total_cost_basis = 0

        for asset in portfolio.assets:
            asset.current_quantity = await asset.get_current_quantity()
            asset.average_cost_basis = await asset.get_average_cost_basis()
            ticker = yf.Ticker(asset.symbol)
            current_price = ticker.history(period="1d")["Close"].iloc[-1]

            asset.current_price = current_price
            asset.holdings = asset.current_quantity * current_price
            asset.total_cost = asset.current_quantity * asset.average_cost_basis
            asset.unrealized_pnl = asset.holdings - asset.total_cost
            if asset.total_cost > 0:
                asset.unrealized_pnl_pct = asset.unrealized_pnl / asset.total_cost
            else:
                asset.unrealized_pnl_pct = 0

            total_holdings_value += asset.holdings
            total_cost_basis += asset.total_cost

        portfolio.total_holdings_value = total_holdings_value
        portfolio.cash = 0.0  # Placeholder for cash
        portfolio.total_portfolio_value = total_holdings_value + portfolio.cash
        portfolio.total_cost_basis = total_cost_basis
        portfolio.total_unrealized_pnl = total_holdings_value - total_cost_basis
        if total_cost_basis > 0:
            portfolio.total_unrealized_pnl_pct = portfolio.total_unrealized_pnl / total_cost_basis
        else:
            portfolio.total_unrealized_pnl_pct = 0

        if portfolio.total_portfolio_value > 0:
            for asset in portfolio.assets:
                asset.weight = (asset.holdings / portfolio.total_portfolio_value) * 100
        else:
            for asset in portfolio.assets:
                asset.weight = 0

        return portfolio
