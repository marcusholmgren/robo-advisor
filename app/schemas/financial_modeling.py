from pydantic import BaseModel
from datetime import date

class FinancialModelingRequest(BaseModel):
    tickers: list[str]
    start_date: date
    end_date: date

class FinancialModelingResponse(BaseModel):
    expected_returns: dict[str, float]
    covariance_matrix: dict[str, dict[str, float]]
