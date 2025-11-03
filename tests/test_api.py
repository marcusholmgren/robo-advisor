"""Tests for the API endpoints."""



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
        portfolio_data = {
            "name": "My Portfolio",
            "description": "A test portfolio"
        }
        response = await client.post("/api/v1/portfolios", json=portfolio_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Portfolio"
        assert data["description"] == "A test portfolio"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_list_portfolios(self, client):
        """Test listing portfolios."""
        # Create some portfolios first
        await client.post("/api/v1/portfolios", json={"name": "Portfolio 1"})
        await client.post("/api/v1/portfolios", json={"name": "Portfolio 2"})

        response = await client.get("/api/v1/portfolios")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_portfolio(self, client):
        """Test getting a specific portfolio."""
        # Create a portfolio
        create_response = await client.post(
            "/api/v1/portfolios",
            json={"name": "Test Portfolio"}
        )
        portfolio_id = create_response.json()["id"]

        # Get the portfolio
        response = await client.get(f"/api/v1/portfolios/{portfolio_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Portfolio"

    async def test_get_nonexistent_portfolio(self, client):
        """Test getting a portfolio that doesn't exist."""
        response = await client.get("/api/v1/portfolios/999")
        assert response.status_code == 404

    async def test_update_portfolio(self, client):
        """Test updating a portfolio."""
        # Create a portfolio
        create_response = await client.post(
            "/api/v1/portfolios",
            json={"name": "Original Name"}
        )
        portfolio_id = create_response.json()["id"]

        # Update the portfolio
        update_data = {"name": "Updated Name", "description": "New description"}
        response = await client.put(
            f"/api/v1/portfolios/{portfolio_id}",
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "New description"

    async def test_delete_portfolio(self, client):
        """Test deleting a portfolio."""
        # Create a portfolio
        create_response = await client.post(
            "/api/v1/portfolios",
            json={"name": "To Delete"}
        )
        portfolio_id = create_response.json()["id"]

        # Delete the portfolio
        response = await client.delete(f"/api/v1/portfolios/{portfolio_id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = await client.get(f"/api/v1/portfolios/{portfolio_id}")
        assert get_response.status_code == 404


class TestAssetEndpoints:
    """Test asset CRUD operations."""

    async def test_create_asset(self, client):
        """Test creating an asset."""
        # First create a portfolio
        portfolio_response = await client.post(
            "/api/v1/portfolios",
            json={"name": "Test Portfolio"}
        )
        portfolio_id = portfolio_response.json()["id"]

        # Create an asset
        asset_data = {
            "portfolio_id": portfolio_id,
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "quantity": "10.5",
            "purchase_price": "150.25"
        }
        response = await client.post("/api/v1/assets", json=asset_data)
        assert response.status_code == 201
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["name"] == "Apple Inc."
        assert float(data["quantity"]) == 10.5
        assert float(data["purchase_price"]) == 150.25

    async def test_create_asset_invalid_portfolio(self, client):
        """Test creating an asset with invalid portfolio."""
        asset_data = {
            "portfolio_id": 999,
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "quantity": "10.5"
        }
        response = await client.post("/api/v1/assets", json=asset_data)
        assert response.status_code == 404

    async def test_list_assets(self, client):
        """Test listing assets."""
        # Create a portfolio
        portfolio_response = await client.post(
            "/api/v1/portfolios",
            json={"name": "Test Portfolio"}
        )
        portfolio_id = portfolio_response.json()["id"]

        # Create some assets
        await client.post("/api/v1/assets", json={
            "portfolio_id": portfolio_id,
            "symbol": "AAPL",
            "name": "Apple",
            "quantity": "10"
        })
        await client.post("/api/v1/assets", json={
            "portfolio_id": portfolio_id,
            "symbol": "GOOGL",
            "name": "Google",
            "quantity": "5"
        })

        # List all assets
        response = await client.get("/api/v1/assets")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_list_assets_by_portfolio(self, client):
        """Test filtering assets by portfolio."""
        # Create two portfolios
        portfolio1 = await client.post(
            "/api/v1/portfolios",
            json={"name": "Portfolio 1"}
        )
        portfolio1_id = portfolio1.json()["id"]
        
        portfolio2 = await client.post(
            "/api/v1/portfolios",
            json={"name": "Portfolio 2"}
        )
        portfolio2_id = portfolio2.json()["id"]

        # Create assets in different portfolios
        await client.post("/api/v1/assets", json={
            "portfolio_id": portfolio1_id,
            "symbol": "AAPL",
            "name": "Apple",
            "quantity": "10"
        })
        await client.post("/api/v1/assets", json={
            "portfolio_id": portfolio2_id,
            "symbol": "GOOGL",
            "name": "Google",
            "quantity": "5"
        })

        # Filter by portfolio
        response = await client.get(f"/api/v1/assets?portfolio_id={portfolio1_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["symbol"] == "AAPL"

    async def test_get_asset(self, client):
        """Test getting a specific asset."""
        # Create a portfolio and asset
        portfolio_response = await client.post(
            "/api/v1/portfolios",
            json={"name": "Test Portfolio"}
        )
        portfolio_id = portfolio_response.json()["id"]

        create_response = await client.post("/api/v1/assets", json={
            "portfolio_id": portfolio_id,
            "symbol": "TSLA",
            "name": "Tesla",
            "quantity": "5"
        })
        asset_id = create_response.json()["id"]

        # Get the asset
        response = await client.get(f"/api/v1/assets/{asset_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "TSLA"

    async def test_update_asset(self, client):
        """Test updating an asset."""
        # Create a portfolio and asset
        portfolio_response = await client.post(
            "/api/v1/portfolios",
            json={"name": "Test Portfolio"}
        )
        portfolio_id = portfolio_response.json()["id"]

        create_response = await client.post("/api/v1/assets", json={
            "portfolio_id": portfolio_id,
            "symbol": "MSFT",
            "name": "Microsoft",
            "quantity": "20"
        })
        asset_id = create_response.json()["id"]

        # Update the asset
        update_data = {"quantity": "25", "purchase_price": "300.50"}
        response = await client.put(
            f"/api/v1/assets/{asset_id}",
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["quantity"]) == 25
        assert float(data["purchase_price"]) == 300.50

    async def test_delete_asset(self, client):
        """Test deleting an asset."""
        # Create a portfolio and asset
        portfolio_response = await client.post(
            "/api/v1/portfolios",
            json={"name": "Test Portfolio"}
        )
        portfolio_id = portfolio_response.json()["id"]

        create_response = await client.post("/api/v1/assets", json={
            "portfolio_id": portfolio_id,
            "symbol": "AMZN",
            "name": "Amazon",
            "quantity": "15"
        })
        asset_id = create_response.json()["id"]

        # Delete the asset
        response = await client.delete(f"/api/v1/assets/{asset_id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = await client.get(f"/api/v1/assets/{asset_id}")
        assert get_response.status_code == 404
