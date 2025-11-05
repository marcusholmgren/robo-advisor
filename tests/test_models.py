from decimal import Decimal
from datetime import datetime, UTC
from app.models import Portfolio, Asset, Trade


class TestPortfolioModel:
    """Test Portfolio model."""

    async def test_create_portfolio(self):
        """Test creating a portfolio."""
        portfolio = await Portfolio.create(name="Test Portfolio", description="A test portfolio")
        assert portfolio.id is not None
        assert portfolio.name == "Test Portfolio"
        assert portfolio.description == "A test portfolio"
        assert portfolio.created_at is not None
        assert portfolio.updated_at is not None

    async def test_portfolio_string_representation(self):
        """Test portfolio string representation."""
        portfolio = await Portfolio.create(name="My Portfolio")
        assert str(portfolio) == "My Portfolio"


class TestAssetAndTradeModels:
    """Tests for the refactored Asset and new Trade models."""

    async def test_create_asset(self):
        """Test creating a simple Asset without trades."""
        portfolio = await Portfolio.create(name="Tech Portfolio")
        asset = await Asset.create(portfolio=portfolio, symbol="MSFT", name="Microsoft Corp.")
        assert asset.id is not None
        assert asset.symbol == "MSFT"
        assert asset.name == "Microsoft Corp."
        # Verify that quantity and price are no longer attributes
        assert not hasattr(asset, "quantity")
        assert not hasattr(asset, "purchase_price")

    async def test_asset_string_representation(self):
        """Test the new asset string representation."""
        portfolio = await Portfolio.create(name="Another Portfolio")
        asset = await Asset.create(portfolio=portfolio, symbol="AMZN", name="Amazon.com Inc.")
        assert str(asset) == f"AMZN in {portfolio.name}"

    async def test_create_trade(self):
        """Test creating a trade for an asset."""
        portfolio = await Portfolio.create(name="Trading Portfolio")
        asset = await Asset.create(portfolio=portfolio, symbol="GOOGL", name="Alphabet Inc.")

        trade_time = datetime.now(UTC)
        trade = await Trade.create(
            asset=asset,
            trade_date=trade_time,
            quantity=Decimal("10"),
            price=Decimal("1350.00"),
            trade_type="BUY",
        )

        assert trade.id is not None
        assert trade.asset_id == asset.id
        assert trade.quantity == Decimal("10")
        assert trade.price == Decimal("1350.00")
        assert trade.trade_type == "BUY"

    async def test_asset_trade_relationship(self):
        """Test the one-to-many relationship from Asset to Trade."""
        portfolio = await Portfolio.create(name="Index Fund")
        asset = await Asset.create(portfolio=portfolio, symbol="SPY", name="SPDR S&P 500 ETF")

        await Trade.create(
            asset=asset,
            trade_date=datetime.now(UTC),
            quantity=Decimal("5"),
            price=Decimal("400.00"),
        )
        await Trade.create(
            asset=asset,
            trade_date=datetime.now(UTC),
            quantity=Decimal("3"),
            price=Decimal("405.50"),
        )

        # Fetch the asset and its related trades
        fetched_asset = await Asset.get(id=asset.id).prefetch_related("trades")
        assert len(fetched_asset.trades) == 2
        assert fetched_asset.trades[0].quantity == Decimal("5")
        assert fetched_asset.trades[1].price == Decimal("405.50")

    async def test_get_current_quantity(self):
        """Test the get_current_quantity method on the Asset model."""
        portfolio = await Portfolio.create(name="Mixed Actions Portfolio")
        asset = await Asset.create(portfolio=portfolio, symbol="TSLA", name="Tesla, Inc.")

        # No trades yet
        assert await asset.get_current_quantity() == 0

        # Add trades
        await Trade.create(
            asset=asset, trade_date=datetime.now(UTC), quantity=Decimal("100"), price=Decimal("200")
        )
        await Trade.create(
            asset=asset, trade_date=datetime.now(UTC), quantity=Decimal("-25"), price=Decimal("210")
        )  # Sell
        await Trade.create(
            asset=asset, trade_date=datetime.now(UTC), quantity=Decimal("50"), price=Decimal("190")
        )

        # 100 - 25 + 50 = 125
        assert await asset.get_current_quantity() == 125

    async def test_get_average_cost_basis(self):
        """Test the get_average_cost_basis method on the Asset model."""
        portfolio = await Portfolio.create(name="Cost Basis Portfolio")
        asset = await Asset.create(portfolio=portfolio, symbol="NVDA", name="NVIDIA Corporation")

        # No trades yet
        assert await asset.get_average_cost_basis() == 0

        # Add trades
        await Trade.create(
            asset=asset, trade_date=datetime.now(UTC), quantity=Decimal("10"), price=Decimal("500")
        )  # Cost: 5000
        await Trade.create(
            asset=asset, trade_date=datetime.now(UTC), quantity=Decimal("20"), price=Decimal("550")
        )  # Cost: 11000
        # This sell should be ignored by the cost basis calculation
        await Trade.create(
            asset=asset, trade_date=datetime.now(UTC), quantity=Decimal("-5"), price=Decimal("600")
        )

        # Total cost = 5000 + 11000 = 16000
        # Total shares (buys only) = 10 + 20 = 30
        # Average cost = 16000 / 30 = 533.333...
        expected_avg_cost = Decimal("16000") / Decimal("30")
        actual_avg_cost = await asset.get_average_cost_basis()

        assert abs(actual_avg_cost - float(expected_avg_cost)) < 0.01
