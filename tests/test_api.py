from datetime import datetime, UTC


class TestRootEndpoints:
    """Test root endpoints."""

    async def test_root(self, client):
        """Test root endpoint."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestPortfolioEndpoints:
    """Test portfolio CRUD operations."""

    async def test_create_portfolio(self, client):
        """Test creating a portfolio."""
        portfolio_data = {"name": "My Portfolio", "description": "A test portfolio"}
        response = await client.post("/api/v1/portfolios", json=portfolio_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Portfolio"
        assert data["description"] == "A test portfolio"
        assert "id" in data

    async def test_list_portfolios(self, client):
        """Test listing portfolios."""
        await client.post("/api/v1/portfolios", json={"name": "Portfolio 1"})
        await client.post("/api/v1/portfolios", json={"name": "Portfolio 2"})
        response = await client.get("/api/v1/portfolios")
        assert response.status_code == 200
        assert len(response.json()) >= 2

    async def test_get_portfolio(self, client):
        """Test getting a specific portfolio."""
        create_response = await client.post("/api/v1/portfolios", json={"name": "Test Portfolio"})
        portfolio_id = create_response.json()["id"]
        response = await client.get(f"/api/v1/portfolios/{portfolio_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Test Portfolio"

    async def test_update_portfolio(self, client):
        """Test updating a portfolio."""
        create_response = await client.post("/api/v1/portfolios", json={"name": "Original Name"})
        portfolio_id = create_response.json()["id"]
        update_data = {"name": "Updated Name"}
        response = await client.put(f"/api/v1/portfolios/{portfolio_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    async def test_delete_portfolio(self, client):
        """Test deleting a portfolio."""
        create_response = await client.post("/api/v1/portfolios", json={"name": "To Delete"})
        portfolio_id = create_response.json()["id"]
        await client.delete(f"/api/v1/portfolios/{portfolio_id}")
        response = await client.get(f"/api/v1/portfolios/{portfolio_id}")
        assert response.status_code == 404


class TestAssetEndpoints:
    """Test asset CRUD operations (post-refactor)."""

    async def test_create_asset(self, client):
        """Test creating a new asset parent."""
        portfolio_res = await client.post(
            "/api/v1/portfolios", json={"name": "Asset Test Portfolio"}
        )
        portfolio_id = portfolio_res.json()["id"]

        asset_data = {"portfolio_id": portfolio_id, "symbol": "AAPL", "name": "Apple Inc."}
        response = await client.post("/api/v1/assets", json=asset_data)

        assert response.status_code == 201
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["name"] == "Apple Inc."
        assert "id" in data

    async def test_get_asset_with_calculations(self, client):
        """Test getting an asset includes calculated fields."""
        portfolio_res = await client.post("/api/v1/portfolios", json={"name": "Calc Portfolio"})
        portfolio_id = portfolio_res.json()["id"]
        asset_res = await client.post(
            "/api/v1/assets", json={"portfolio_id": portfolio_id, "symbol": "TSLA", "name": "Tesla"}
        )
        asset_id = asset_res.json()["id"]

        # Add a trade to the asset
        trade_data = {
            "asset_id": asset_id,
            "trade_date": datetime.now(UTC).isoformat(),
            "quantity": "10",
            "price": "250.00",
            "trade_type": "BUY",
        }
        await client.post("/api/v1/trades", json=trade_data)

        response = await client.get(f"/api/v1/assets/{asset_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "TSLA"
        assert data["current_quantity"] == 10.0
        assert data["average_cost_basis"] == 250.0

    async def test_update_asset(self, client):
        """Test updating an asset's name."""
        portfolio_res = await client.post("/api/v1/portfolios", json={"name": "Update Portfolio"})
        portfolio_id = portfolio_res.json()["id"]
        asset_res = await client.post(
            "/api/v1/assets",
            json={"portfolio_id": portfolio_id, "symbol": "MSFT", "name": "Microsoft"},
        )
        asset_id = asset_res.json()["id"]

        update_data = {"name": "Microsoft Corporation"}
        response = await client.put(f"/api/v1/assets/{asset_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Microsoft Corporation"


class TestTradeEndpoints:
    """Test trade CRUD operations."""

    async def test_create_trade(self, client):
        """Test creating a trade for an asset."""
        portfolio_res = await client.post("/api/v1/portfolios", json={"name": "Trade Portfolio"})
        portfolio_id = portfolio_res.json()["id"]
        asset_res = await client.post(
            "/api/v1/assets",
            json={"portfolio_id": portfolio_id, "symbol": "NVDA", "name": "Nvidia"},
        )
        asset_id = asset_res.json()["id"]

        trade_data = {
            "asset_id": asset_id,
            "trade_date": datetime.now(UTC).isoformat(),
            "quantity": "5",
            "price": "550.50",
            "trade_type": "BUY",
        }
        response = await client.post("/api/v1/trades", json=trade_data)
        assert response.status_code == 201
        data = response.json()
        assert data["quantity"] == "5"
        assert data["price"] == "550.5"
        assert "id" in data

    async def test_list_trades_for_asset(self, client):
        """Test listing all trades for a specific asset."""
        portfolio_res = await client.post(
            "/api/v1/portfolios", json={"name": "List Trades Portfolio"}
        )
        portfolio_id = portfolio_res.json()["id"]
        asset_res = await client.post(
            "/api/v1/assets",
            json={"portfolio_id": portfolio_id, "symbol": "GOOGL", "name": "Alphabet"},
        )
        asset_id = asset_res.json()["id"]

        # Create two trades
        await client.post(
            "/api/v1/trades",
            json={
                "asset_id": asset_id,
                "trade_date": datetime.now(UTC).isoformat(),
                "quantity": "2",
                "price": "1300",
            },
        )
        await client.post(
            "/api/v1/trades",
            json={
                "asset_id": asset_id,
                "trade_date": datetime.now(UTC).isoformat(),
                "quantity": "3",
                "price": "1350",
            },
        )

        response = await client.get(f"/api/v1/assets/{asset_id}/trades")
        assert response.status_code == 200
        assert len(response.json()) == 2

    async def test_delete_trade(self, client):
        """Test deleting a trade."""
        portfolio_res = await client.post(
            "/api/v1/portfolios", json={"name": "Delete Trade Portfolio"}
        )
        portfolio_id = portfolio_res.json()["id"]
        asset_res = await client.post(
            "/api/v1/assets",
            json={"portfolio_id": portfolio_id, "symbol": "AMZN", "name": "Amazon"},
        )
        asset_id = asset_res.json()["id"]
        trade_res = await client.post(
            "/api/v1/trades",
            json={
                "asset_id": asset_id,
                "trade_date": datetime.now(UTC).isoformat(),
                "quantity": "1",
                "price": "180",
            },
        )
        trade_id = trade_res.json()["id"]

        del_response = await client.delete(f"/api/v1/trades/{trade_id}")
        assert del_response.status_code == 204

        # Verify the asset now has zero quantity
        asset_response = await client.get(f"/api/v1/assets/{asset_id}")
        assert asset_response.json()["current_quantity"] == 0
