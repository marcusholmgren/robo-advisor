import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.services.financial_modeling_service import FinancialModelingService
import pandas as pd
import numpy as np
from unittest.mock import patch

client = TestClient(app)


@pytest.fixture
def financial_modeling_service():
    return FinancialModelingService()


@pytest.fixture
def sample_tickers():
    return ["AAPL", "MSFT"]


@pytest.fixture
def sample_dates():
    end_date = date.today()
    start_date = end_date - timedelta(days=365 * 2)  # 2 years of data
    return start_date, end_date


@pytest.fixture
def mock_get_historical_data():
    with patch(
        "app.services.financial_modeling_service.FinancialModelingService.get_historical_data"
    ) as mock_method:
        # Create a sample DataFrame for mocking what get_historical_data should return
        dates = pd.bdate_range(end=date.today(), periods=100)
        data = {
            "AAPL": np.random.rand(100) * 100 + 100,
            "MSFT": np.random.rand(100) * 50 + 200,
        }
        mock_df = pd.DataFrame(data, index=dates)
        mock_method.return_value = mock_df
        yield mock_method


@pytest.mark.asyncio
async def test_get_historical_data(
    financial_modeling_service, sample_tickers, sample_dates, mock_get_historical_data
):
    start_date, end_date = sample_dates
    data = financial_modeling_service.get_historical_data(
        sample_tickers, str(start_date), str(end_date)
    )
    assert not data.empty
    assert all(ticker in data.columns for ticker in sample_tickers)
    assert len(data) > 0
    mock_get_historical_data.assert_called_once()


@pytest.mark.asyncio
async def test_calculate_returns(
    financial_modeling_service, sample_tickers, sample_dates, mock_get_historical_data
):
    start_date, end_date = sample_dates
    historical_data = financial_modeling_service.get_historical_data(
        sample_tickers, str(start_date), str(end_date)
    )
    returns = financial_modeling_service.calculate_returns(historical_data)
    assert not returns.empty
    assert all(ticker in returns.columns for ticker in sample_tickers)
    assert len(returns) == len(historical_data) - 1  # One less row due to pct_change


@pytest.mark.asyncio
async def test_calculate_expected_returns(
    financial_modeling_service, sample_tickers, sample_dates, mock_get_historical_data
):
    start_date, end_date = sample_dates
    historical_data = financial_modeling_service.get_historical_data(
        sample_tickers, str(start_date), str(end_date)
    )
    returns = financial_modeling_service.calculate_returns(historical_data)
    expected_returns = financial_modeling_service.calculate_expected_returns(returns)
    assert not expected_returns.empty
    assert all(ticker in expected_returns.index for ticker in sample_tickers)
    assert isinstance(expected_returns, pd.Series)


@pytest.mark.asyncio
async def test_calculate_covariance_matrix(
    financial_modeling_service, sample_tickers, sample_dates, mock_get_historical_data
):
    start_date, end_date = sample_dates
    historical_data = financial_modeling_service.get_historical_data(
        sample_tickers, str(start_date), str(end_date)
    )
    returns = financial_modeling_service.calculate_returns(historical_data)
    covariance_matrix = financial_modeling_service.calculate_covariance_matrix(returns)
    assert not covariance_matrix.empty
    assert all(ticker in covariance_matrix.columns for ticker in sample_tickers)
    assert all(ticker in covariance_matrix.index for ticker in sample_tickers)
    assert isinstance(covariance_matrix, pd.DataFrame)
    assert covariance_matrix.shape == (len(sample_tickers), len(sample_tickers))


@pytest.mark.asyncio
async def test_financial_modeling_endpoint_success(
    sample_tickers, sample_dates, mock_get_historical_data
):
    start_date, end_date = sample_dates
    response = client.post(
        "/api/v1/financial-modeling/",
        json={"tickers": sample_tickers, "start_date": str(start_date), "end_date": str(end_date)},
    )
    assert response.status_code == 200
    data = response.json()
    assert "expected_returns" in data
    assert "covariance_matrix" in data
    assert all(ticker in data["expected_returns"] for ticker in sample_tickers)
    assert all(ticker in data["covariance_matrix"] for ticker in sample_tickers)


@pytest.mark.asyncio
async def test_financial_modeling_endpoint_no_data(sample_dates, mock_get_historical_data):
    # Configure mock to return empty DataFrame for this specific test
    mock_get_historical_data.return_value = pd.DataFrame()
    start_date, end_date = sample_dates
    response = client.post(
        "/api/v1/financial-modeling/",
        json={
            "tickers": ["NONEXISTENTTICKER123"],
            "start_date": str(start_date),
            "end_date": str(end_date),
        },
    )
    assert response.status_code == 404
    assert "No historical data found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_portfolio_analysis_endpoint_success(mock_get_historical_data):
    # 1. Create a portfolio
    portfolio_response = client.post(
        "/api/v1/portfolios",
        json={
            "name": "Test Portfolio for Analysis",
            "description": "A portfolio for testing the analysis endpoint.",
        },
    )
    assert portfolio_response.status_code == 201, portfolio_response.json()
    portfolio_id = portfolio_response.json()["id"]

    # 2. Add assets to the portfolio
    assets_to_create = [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "quantity": 10,
        },
        {
            "symbol": "MSFT",
            "name": "Microsoft Corp.",
            "quantity": 5,
        },
    ]
    for asset_data in assets_to_create:
        asset_response = client.post(f"/api/v1/portfolios/{portfolio_id}/assets", json=asset_data)
        assert asset_response.status_code == 201, asset_response.json()

    # 3. Call the analysis endpoint
    analysis_response = client.post(
        f"/api/v1/portfolios/{portfolio_id}/analysis", json={"risk_free_rate": 0.01}
    )

    # 4. Assert the response
    assert analysis_response.status_code == 200
    data = analysis_response.json()
    assert "sharpe_ratio" in data
    assert "tangency_portfolio_weights" in data
    assert "markowitz_bullet_plot" in data
    assert isinstance(data["sharpe_ratio"], float)
    assert isinstance(data["tangency_portfolio_weights"], dict)
    assert isinstance(data["markowitz_bullet_plot"], str)

    # Clean up the created portfolio and assets
    delete_portfolio_response = client.delete(f"/api/v1/portfolios/{portfolio_id}")
    assert delete_portfolio_response.status_code == 204
