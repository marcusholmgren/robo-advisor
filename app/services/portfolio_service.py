"""Service for portfolio-related operations."""

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

        total_portfolio_value = 0
        for asset in portfolio.assets:
            asset.current_quantity = await asset.get_current_quantity()
            ticker = yf.Ticker(asset.symbol)
            current_price = ticker.history(period="1d")["Close"].iloc[-1]
            asset.holdings = asset.current_quantity * current_price
            total_portfolio_value += asset.holdings

        if total_portfolio_value > 0:
            for asset in portfolio.assets:
                asset.weight = (asset.holdings / total_portfolio_value) * 100
        else:
            for asset in portfolio.assets:
                asset.weight = 0

        return portfolio
