import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

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

    def calculate_sharpe_ratio(self, expected_return, portfolio_volatility, risk_free_rate):
        """Calculates the Sharpe ratio."""
        return (expected_return - risk_free_rate) / portfolio_volatility

    def find_tangency_portfolio(self, mu, Cov, r_f):
        try:
            Cov_inv = np.linalg.inv(Cov)
        except np.linalg.LinAlgError:
            Cov_inv = np.linalg.pinv(Cov)
        ones = np.ones(len(mu))
        A = ones @ Cov_inv @ ones
        B = ones @ Cov_inv @ mu
        mu_excess = mu - r_f * ones
        denominator = B - r_f * A
        numerator = Cov_inv @ mu_excess
        w_tan = numerator / denominator
        return w_tan

    def mu_sigma_portfolio(self, weights, means, Cov):
        mu_p = np.dot(weights, means)
        sigma_p = (weights @ Cov @ weights) ** 0.5
        return mu_p, sigma_p

    def plot_capital_market_line(self, mu_tan, sigma_tan, r_f, x_limit):
        sharpe_ratio = (mu_tan - r_f) / sigma_tan
        print(f"\n--- Tangency Portfolio ---")
        print(f"Max Sharpe Ratio: {sharpe_ratio:.4f}")
        print(f"Return (μ): {mu_tan:.4f}")
        print(f"Volatility (σ): {sigma_tan:.4f}")

        x_cml = np.linspace(0, x_limit, 100)
        y_cml = r_f + sharpe_ratio * x_cml

        plt.plot(x_cml, y_cml, color='red', linestyle='-', lw=2.5, label='Capital Market Line (CML)')
        plt.plot(sigma_tan, mu_tan, 'r*', markersize=15, label='Tangency Portfolio')
        plt.plot(0, r_f, 'ro', markersize=8)
        plt.annotate('Risk-Free Asset', (0.01, r_f), va='center')


    def plot_min_var_frontier(self, mu, Cov):
        A, B, C = self.computer_ABC(mu, Cov)

        # Check for valid determinant
        if (A * C - B * B) <= 0:
            print("Error: Cannot compute frontier, check data.")
            return

        # Global Minimum Variance (GMV) return
        gmv_return = B / A

        # Plot inefficient part of the frontier
        y = np.linspace(0, gmv_return, 100)
        x = np.sqrt((A * y * y - 2 * B * y + C) / (A * C - B * B))
        plt.plot(x, y, color='black', lw=2.5, linestyle='--')

        # Plot efficient frontier (from GMV up to plot limit)
        # --- PLOTTING FIX 2: Adjusted linspace upper bound ---
        y = np.linspace(gmv_return, 0.25, 100)
        x = np.sqrt((A * y * y - 2 * B * y + C) / (A * C - B * B))
        plt.plot(x, y, color='black', lw=2.5, label='Efficient Frontier')
        plt.legend()

    def plot_random_portfolios(self, mu, Cov, n_simulations):
        n_assets = len(mu)
        mu_p_sims = []
        sigma_p_sims = []
        for i in range(n_simulations):
            w = self.random_weights(n_assets)
            mu_p, sigma_p = self.mu_sigma_portfolio(w, mu, Cov)
            mu_p_sims.append(mu_p)
            sigma_p_sims.append(sigma_p)
        plt.scatter(sigma_p_sims, mu_p_sims, s=12, alpha=0.6)

    def plot_points(self, mu, sigma, stocks):
        plt.figure(figsize=(8, 6))
        plt.scatter(sigma, mu, c='black')
        # --- PLOTTING FIX 1: Adjusted xlim ---
        plt.xlim(0, 0.75)
        plt.ylim(0, 0.25)
        plt.ylabel('Mean (Annual Expected Return)')
        plt.xlabel('Standard Deviation (Annual Volatility)')
        sigma = pd.Series(sigma, index=mu.index)
        for i, stock in enumerate(stocks):
            plt.annotate(stock, (sigma.iloc[i], mu.iloc[i]), ha='center',
                         va='bottom', weight='bold')

    def computer_ABC(self, mu, Cov):
        n_assets = len(mu)
        # Handle potential singularity if Cov is not invertible
        try:
            Cov_inv = np.linalg.inv(Cov)
        except np.linalg.LinAlgError:
            print("Error: Covariance matrix is singular, cannot be inverted.")
            # Use pseudo-inverse as a fallback
            Cov_inv = np.linalg.pinv(Cov)

        ones = np.ones(n_assets)
        A = ones @ Cov_inv @ ones
        B = ones @ Cov_inv @ mu
        C = mu @ Cov_inv @ mu
        return A, B, C

    def random_weights(self, n_assets):
        k = np.random.randn(n_assets)
        return k / sum(k)

    def generate_markowitz_bullet(self, mu, Cov, r_f, stocks):
        # --- MAIN SCRIPT ---
        n_simulations = 5000
        plot_limit_x = 0.75
        plot_limit_y = 0.25

        # Define the risk-free rate
        r_f = 0.01

        # --- 1. Find the Tangency Portfolio ---
        w_tan = self.find_tangency_portfolio(mu, Cov, r_f)
        mu_tan, sigma_tan = self.mu_sigma_portfolio(w_tan, mu, Cov)

        print("Tangency Portfolio Weights:")
        for i, stock in enumerate(stocks):
            print(f"{stock}: {w_tan[i]:.4f}")

        # --- 2. Plot everything ---
        self.plot_points(mu, np.diag(Cov) ** 0.5, stocks)
        self.plot_random_portfolios(mu, Cov, n_simulations)
        self.plot_min_var_frontier(mu, Cov)

        # Plot the CML and the tangency point
        self.plot_capital_market_line(mu_tan, sigma_tan, r_f, plot_limit_x)

        plt.title('Mean-Variance Optimization with Capital Market Line')
        plt.legend()

        # Save the plot to a BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Encode the image in base64
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')

        # Close the buffer and the plot
        buf.close()
        plt.close()

        return image_base64
