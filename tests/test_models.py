"""Tests for database models."""

from decimal import Decimal
from app.models import Portfolio, Asset


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


class TestAssetModel:
    """Test Asset model."""

    async def test_create_asset(self):
        """Test creating an asset."""
        # Create a portfolio first
        portfolio = await Portfolio.create(name="Test Portfolio")

        # Create an asset
        asset = await Asset.create(
            portfolio=portfolio,
            symbol="AAPL",
            name="Apple Inc.",
            quantity=Decimal("10.5"),
            purchase_price=Decimal("150.25"),
        )

        assert asset.id is not None
        assert asset.symbol == "AAPL"
        assert asset.name == "Apple Inc."
        assert asset.quantity == Decimal("10.5")
        assert asset.purchase_price == Decimal("150.25")
        assert asset.created_at is not None
        assert asset.updated_at is not None

    async def test_asset_portfolio_relationship(self):
        """Test asset-portfolio relationship."""
        # Create a portfolio
        portfolio = await Portfolio.create(name="Test Portfolio")

        # Create an asset
        asset = await Asset.create(
            portfolio=portfolio, symbol="GOOGL", name="Google", quantity=Decimal("5")
        )

        # Fetch the asset with portfolio
        fetched_asset = await Asset.get(id=asset.id).prefetch_related("portfolio")
        assert fetched_asset.portfolio.name == "Test Portfolio"

    async def test_asset_string_representation(self):
        """Test asset string representation."""
        portfolio = await Portfolio.create(name="Test Portfolio")
        asset = await Asset.create(
            portfolio=portfolio, symbol="TSLA", name="Tesla Inc.", quantity=Decimal("3")
        )
        assert str(asset) == "TSLA - Tesla Inc."
