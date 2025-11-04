import pytest
import pandas as pd
import numpy as np
from app.services.financial_modeling_service import FinancialModelingService

@pytest.fixture
def financial_modeling_service():
    return FinancialModelingService()

@pytest.fixture
def mock_daily_returns():
    data = {
        'Asset1': [0.01, 0.02, -0.01, 0.005, -0.005],
        'Asset2': [0.02, 0.01, 0.005, -0.01, 0.015],
        'Asset3': [-0.005, 0.005, 0.01, 0.02, -0.01]
    }
    return pd.DataFrame(data)

@pytest.fixture
def mock_historical_data():
    data = {
        'Asset1': [100, 101, 103.02, 101.9898, 102.509749],
        'Asset2': [200, 204, 206.04, 204.0796, 207.140892],
        'Asset3': [300, 298.5, 300, 303, 300]
    }
    return pd.DataFrame(data)

def test_calculate_returns(financial_modeling_service, mock_historical_data):
    returns = financial_modeling_service.calculate_returns(mock_historical_data)
    assert isinstance(returns, pd.DataFrame)
    assert not returns.empty
    assert returns.shape == (4, 3)

def test_calculate_expected_returns(financial_modeling_service, mock_daily_returns):
    expected_returns = financial_modeling_service.calculate_expected_returns(mock_daily_returns)
    assert isinstance(expected_returns, pd.Series)
    assert not expected_returns.empty
    assert expected_returns.shape == (3,)

def test_calculate_covariance_matrix(financial_modeling_service, mock_daily_returns):
    covariance_matrix = financial_modeling_service.calculate_covariance_matrix(mock_daily_returns)
    assert isinstance(covariance_matrix, pd.DataFrame)
    assert not covariance_matrix.empty
    assert covariance_matrix.shape == (3, 3)

def test_calculate_sharpe_ratio(financial_modeling_service):
    sharpe_ratio = financial_modeling_service.calculate_sharpe_ratio(0.1, 0.2, 0.05)
    assert isinstance(sharpe_ratio, float)
    assert sharpe_ratio == 0.25

def test_find_tangency_portfolio(financial_modeling_service, mock_daily_returns):
    mu = financial_modeling_service.calculate_expected_returns(mock_daily_returns)
    cov = financial_modeling_service.calculate_covariance_matrix(mock_daily_returns)
    r_f = 0.01
    weights = financial_modeling_service.find_tangency_portfolio(mu, cov, r_f)
    assert isinstance(weights, np.ndarray)
    assert weights.shape == (3,)

def test_mu_sigma_portfolio(financial_modeling_service, mock_daily_returns):
    mu = financial_modeling_service.calculate_expected_returns(mock_daily_returns)
    cov = financial_modeling_service.calculate_covariance_matrix(mock_daily_returns)
    weights = np.array([0.5, 0.3, 0.2])
    mu_p, sigma_p = financial_modeling_service.mu_sigma_portfolio(weights, mu, cov)
    assert isinstance(mu_p, float)
    assert isinstance(sigma_p, float)

def test_compute_abc(financial_modeling_service, mock_daily_returns):
    mu = financial_modeling_service.calculate_expected_returns(mock_daily_returns)
    cov = financial_modeling_service.calculate_covariance_matrix(mock_daily_returns)
    A, B, C = financial_modeling_service.compute_ABC(mu, cov)
    assert isinstance(A, float)
    assert isinstance(B, float)
    assert isinstance(C, float)
