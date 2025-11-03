import yfinance as yf
import pandas as pd
import numpy as np

class FinancialModelingService:
    def __init__(self):
        pass

    def get_historical_data(self, tickers: list[str], start_date: str, end_date: str) -> pd.DataFrame:
        """Fetches historical stock data for a list of tickers."""
        data = yf.download(tickers, start=start_date, end=end_date)
        if data.empty:
            return pd.DataFrame()

        # Extract 'Close' prices
        if isinstance(data.columns, pd.MultiIndex):
            close_data = data['Close']
        elif 'Close' in data.columns:
            close_data = data[['Close']]
        else:
            return pd.DataFrame()

        # Drop columns (tickers) that are all NaN (no data found for them)
        close_data = close_data.dropna(axis=1, how='all')

        if close_data.empty:
            return pd.DataFrame()

        return close_data

    def calculate_returns(self, historical_data: pd.DataFrame) -> pd.DataFrame:
        """Calculates daily returns from historical adjusted close prices."""
        return historical_data.pct_change().dropna()

    def calculate_expected_returns(self, daily_returns: pd.DataFrame, trading_days_per_year: int = 252) -> pd.Series:
        """Calculates expected annual returns."""
        return daily_returns.mean() * trading_days_per_year

    def calculate_covariance_matrix(self, daily_returns: pd.DataFrame, trading_days_per_year: int = 252) -> pd.DataFrame:
        """Calculates the annual covariance matrix of returns."""
        return daily_returns.cov() * trading_days_per_year
