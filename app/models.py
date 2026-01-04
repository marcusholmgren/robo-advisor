"""
/home/marcus/code/marcus/robo-advisor/app/models.py
Database models using TortoiseORM.
This file defines the database schema for portfolios, assets, trades, and risk profiles.
RELEVANT FILES: app/database.py, app/routes.py, app/schemas/portfolio.py
"""

from tortoise import fields
from tortoise.models import Model
from tortoise.functions import Sum
from tortoise.expressions import F


class Portfolio(Model):
    """Portfolio model representing an investment portfolio."""

    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "portfolios"

    def __str__(self):
        return self.name


class Asset(Model):
    """
    Asset model representing a unique holding (e.g., "AAPL")
    within a specific portfolio.

    This model NO LONGER stores quantity or price. It acts
    as the "parent" for all trades of this symbol.
    """

    id = fields.IntField(primary_key=True)
    portfolio = fields.ForeignKeyField("models.Portfolio", related_name="assets")
    symbol = fields.CharField(max_length=20)
    name = fields.CharField(max_length=255)  # You can keep the name for easy reference
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "assets"
        # Ensure a portfolio can only have one "Asset" entry per symbol
        unique_together = ("portfolio", "symbol")

    def __str__(self):
        return f"{self.symbol} in {self.portfolio.name}"

    # --- NEW METHODS ---
    # You can add helper methods to calculate current state

    async def get_current_quantity(self) -> float:
        """Calculates the total quantity from all associated trades."""
        # This performs a SUM(quantity) in the database
        result = await self.trades.all().annotate(total_quantity=Sum("quantity")).first()

        return result.total_quantity if result and result.total_quantity is not None else 0

    async def get_average_cost_basis(self) -> float:
        """Calculates the average purchase price (simplified)."""

        # This is a simplified calculation. Real-world scenarios
        # need to account for FIFO/LIFO and how sales affect the basis.

        # Get total cost and total quantity for BUYS only
        buys = self.trades.filter(quantity__gt=0)

        aggregation = await buys.annotate(
            total_cost=Sum(F("quantity") * F("price")), total_shares=Sum("quantity")
        ).first()

        if not aggregation or aggregation.total_shares is None or aggregation.total_shares == 0:
            return 0

        return aggregation.total_cost / aggregation.total_shares


class Trade(Model):
    """
    NEW MODEL: Represents a single transaction (buy, sell, etc.)
    for an asset in a portfolio.
    """

    id = fields.IntField(primary_key=True)
    asset = fields.ForeignKeyField("models.Asset", related_name="trades")

    # User-supplied date of the transaction
    trade_date = fields.DatetimeField()

    # Positive for BUY, Negative for SELL
    quantity = fields.DecimalField(max_digits=20, decimal_places=8)

    # Price per unit at the time of the trade
    price = fields.DecimalField(max_digits=20, decimal_places=2)

    # Type of trade (optional but recommended)
    trade_type = fields.CharField(max_length=10, default="BUY")  # e.g., "BUY", "SELL", "DIVIDEND"

    # When the trade was entered into the system (for auditing)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "trades"

    def __str__(self):
        action = "Buy" if self.quantity > 0 else "Sell"
        return f"{action} {abs(self.quantity)} {self.asset.symbol} @ {self.price}"


class RiskProfile(Model):
    """Risk profile model representing the user's risk tolerance."""

    id = fields.IntField(primary_key=True)
    portfolio = fields.OneToOneField("models.Portfolio", related_name="risk_profile")
    risk_score = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "risk_profiles"

    def __str__(self):
        return f"Risk profile for portfolio {self.portfolio.name}"
