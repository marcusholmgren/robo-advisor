"""
/home/marcus/code/marcus/robo-advisor/app/services/portfolio_service.py
Service for portfolio-related operations.
This file handles complex portfolio logic, including calculating holdings and weights.
RELEVANT FILES: app/models.py, app/routes.py, app/schemas/portfolio.py
"""

import asyncio
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

        tickers = [asset.symbol for asset in portfolio.assets]
        prices = {}
        if tickers:
            def fetch_prices():
                data = yf.download(tickers, period="1d")
                result_prices = {}
                if "Close" in data:
                    close_data = data["Close"]
                    if len(tickers) == 1:
                        # yfinance returns a Series if only one ticker is requested
                        if not close_data.empty:
                            result_prices[tickers[0]] = float(close_data.iloc[-1])
                    else:
                        for t in tickers:
                            if t in close_data and not close_data[t].dropna().empty:
                                result_prices[t] = float(close_data[t].dropna().iloc[-1])
                return result_prices

            prices = await asyncio.to_thread(fetch_prices)

        for asset in portfolio.assets:
            # Aggregate calculations directly in memory to avoid N+1 queries
            total_quantity = 0.0
            total_cost_for_buys = 0.0
            total_shares_bought = 0.0

            for trade in asset.trades:
                total_quantity += float(trade.quantity)
                if trade.quantity > 0:
                    total_shares_bought += float(trade.quantity)
                    total_cost_for_buys += float(trade.quantity) * float(trade.price)

            asset.current_quantity = total_quantity
            asset.average_cost_basis = total_cost_for_buys / total_shares_bought if total_shares_bought > 0 else 0.0

            current_price = prices.get(asset.symbol, 0.0)

            asset.current_price = current_price
            asset.holdings = float(asset.current_quantity) * current_price
            asset.total_cost = float(asset.current_quantity) * asset.average_cost_basis
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
