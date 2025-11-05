"""API routes for the robo-advisor application."""

from typing import List
from fastapi import APIRouter, HTTPException, status
from tortoise.exceptions import DoesNotExist

from app.models import Portfolio, Asset, Trade
from app.services import risk_assessment_service
from app.schemas.risk_profile import RiskProfile, RiskProfileCreate
from app.schemas.financial_modeling import (
    FinancialModelingRequest,
    FinancialModelingResponse,
    PortfolioAnalysisRequest,
    PortfolioAnalysisResponse,
)
from app.services.financial_modeling_service import FinancialModelingService
from app import schemas
from app.schemas.portfolio import Trade as TradeSchema, TradeCreate, TradeBase

router = APIRouter()

financial_modeling_service = FinancialModelingService()


@router.post("/risk-profiles/", response_model=RiskProfile, status_code=status.HTTP_201_CREATED)
async def create_risk_profile_route(risk_profile: RiskProfileCreate):
    """Create a new risk profile."""
    return await risk_assessment_service.create_risk_profile(risk_profile)


@router.post(
    "/financial-modeling/", response_model=FinancialModelingResponse, status_code=status.HTTP_200_OK
)
async def get_financial_metrics(request: FinancialModelingRequest):
    """Calculate expected returns and covariance matrix for given tickers and date range."""
    historical_data = financial_modeling_service.get_historical_data(
        request.tickers, str(request.start_date), str(request.end_date)
    )
    if historical_data.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No historical data found for the given tickers and date range.",
        )

    daily_returns = financial_modeling_service.calculate_returns(historical_data)
    expected_returns = financial_modeling_service.calculate_expected_returns(daily_returns)
    covariance_matrix = financial_modeling_service.calculate_covariance_matrix(daily_returns)

    return FinancialModelingResponse(
        expected_returns=expected_returns.to_dict(), covariance_matrix=covariance_matrix.to_dict()
    )


# Portfolio endpoints
@router.get("/portfolios", response_model=List[schemas.Portfolio])
async def list_portfolios():
    """List all portfolios."""
    portfolios = await Portfolio.all()
    return portfolios


@router.get("/portfolios/{portfolio_id}", response_model=schemas.Portfolio)
async def get_portfolio(portfolio_id: int):
    """Get a specific portfolio by ID."""
    try:
        portfolio = await Portfolio.get(id=portfolio_id)
        return portfolio
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found",
        )


@router.post("/portfolios", response_model=schemas.Portfolio, status_code=status.HTTP_201_CREATED)
async def create_portfolio(portfolio: schemas.PortfolioCreate):
    """Create a new portfolio."""
    portfolio_obj = await Portfolio.create(**portfolio.model_dump())
    return portfolio_obj


@router.put("/portfolios/{portfolio_id}", response_model=schemas.Portfolio)
async def update_portfolio(portfolio_id: int, portfolio: schemas.PortfolioUpdate):
    """Update an existing portfolio."""
    try:
        portfolio_obj = await Portfolio.get(id=portfolio_id)
        update_data = portfolio.model_dump(exclude_unset=True)
        await portfolio_obj.update_from_dict(update_data).save()
        return portfolio_obj
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found",
        )


@router.delete("/portfolios/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(portfolio_id: int):
    """Delete a portfolio."""
    try:
        portfolio = await Portfolio.get(id=portfolio_id)
        await portfolio.delete()
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found",
        )


@router.post("/portfolios/{portfolio_id}/analysis", response_model=PortfolioAnalysisResponse)
async def portfolio_analysis(portfolio_id: int, request: PortfolioAnalysisRequest):
    """Perform a financial analysis of a portfolio."""
    try:
        portfolio = await Portfolio.get(id=portfolio_id).prefetch_related("assets")
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found",
        )

    tickers = [asset.symbol for asset in portfolio.assets]
    if not tickers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Portfolio has no assets to analyze.",
        )

    # Fetch historical data
    # TODO: Make the date range configurable
    historical_data = financial_modeling_service.get_historical_data(
        tickers, "2020-01-01", "2023-01-01"
    )
    if historical_data.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No historical data found for the given tickers and date range.",
        )

    # Perform calculations
    daily_returns = financial_modeling_service.calculate_returns(historical_data)
    mu = financial_modeling_service.calculate_expected_returns(daily_returns)
    Cov = financial_modeling_service.calculate_covariance_matrix(daily_returns)

    # Calculate Sharpe Ratio for the tangency portfolio
    w_tan = financial_modeling_service.find_tangency_portfolio(mu, Cov, request.risk_free_rate)
    mu_tan, sigma_tan = financial_modeling_service.mu_sigma_portfolio(w_tan, mu, Cov)
    sharpe_ratio = financial_modeling_service.calculate_sharpe_ratio(
        mu_tan, sigma_tan, request.risk_free_rate
    )

    # Generate Markowitz Bullet Plot
    plot_base64 = financial_modeling_service.generate_markowitz_bullet(
        mu, Cov, request.risk_free_rate, tickers
    )

    return PortfolioAnalysisResponse(
        sharpe_ratio=sharpe_ratio,
        tangency_portfolio_weights=dict(zip(tickers, w_tan)),
        markowitz_bullet_plot=plot_base64,
    )


# Asset endpoints
@router.get("/portfolios/{portfolio_id}/assets", response_model=List[schemas.Asset])
async def list_assets(portfolio_id: int):
    """List all assets for a specific portfolio."""
    assets_from_db = await Asset.filter(portfolio_id=portfolio_id)

    # Create a list of Pydantic models, calculating dynamic fields for each asset
    asset_schemas = []
    for asset in assets_from_db:
        asset_schema = schemas.Asset.model_validate(asset)
        asset_schema.current_quantity = await asset.get_current_quantity()
        asset_schema.average_cost_basis = await asset.get_average_cost_basis()
        asset_schemas.append(asset_schema)

    return asset_schemas


@router.get("/assets/{asset_id}", response_model=schemas.Asset)
async def get_asset(asset_id: int):
    """
    Get a specific asset by ID, including its calculated
    quantity and average cost basis.
    """
    try:
        asset = await Asset.get(id=asset_id)
        # Create a Pydantic model from the Tortoise model
        asset_schema = schemas.Asset.model_validate(asset)
        # Calculate and set the dynamic fields
        asset_schema.current_quantity = await asset.get_current_quantity()
        asset_schema.average_cost_basis = await asset.get_average_cost_basis()
        return asset_schema
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset with id {asset_id} not found"
        )


@router.post("/assets", response_model=schemas.Asset, status_code=status.HTTP_201_CREATED)
async def create_asset(asset: schemas.AssetCreate):
    """
    Create a new asset parent. This does not include any trades.
    A trade must be added separately.
    """
    try:
        await Portfolio.get(id=asset.portfolio_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {asset.portfolio_id} not found",
        )

    # Check if an asset with the same symbol already exists in the portfolio
    existing_asset = await Asset.filter(
        portfolio_id=asset.portfolio_id, symbol=asset.symbol
    ).first()
    if existing_asset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Asset with symbol '{asset.symbol}' already exists in this portfolio.",
        )

    asset_obj = await Asset.create(**asset.model_dump())
    return asset_obj


@router.put("/assets/{asset_id}", response_model=schemas.Asset)
async def update_asset(asset_id: int, asset: schemas.AssetUpdate):
    """Update an asset's details (e.g., name or symbol)."""
    try:
        asset_obj = await Asset.get(id=asset_id)
        update_data = asset.model_dump(exclude_unset=True)
        await asset_obj.update_from_dict(update_data).save()
        return asset_obj
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset with id {asset_id} not found"
        )


@router.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: int):
    """
    Delete an asset and all its associated trades.
    """
    try:
        asset = await Asset.get(id=asset_id)
        # The database cascade should handle deleting related trades
        await asset.delete()
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset with id {asset_id} not found"
        )


# --- Trade Endpoints ---


@router.post("/trades", response_model=TradeSchema, status_code=status.HTTP_201_CREATED)
async def create_trade(trade: TradeCreate):
    """Create a new trade for an asset."""
    try:
        # Ensure the asset exists before creating a trade for it
        await Asset.get(id=trade.asset_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {trade.asset_id} not found. Cannot create trade.",
        )

    trade_obj = await Trade.create(**trade.model_dump())
    return trade_obj


@router.get("/assets/{asset_id}/trades", response_model=List[TradeSchema])
async def list_trades_for_asset(asset_id: int):
    """List all trades for a specific asset."""
    try:
        # Ensure the asset exists
        asset = await Asset.get(id=asset_id)
        # Fetch all trades related to this asset
        trades = await Trade.filter(asset_id=asset.id).order_by("-trade_date")
        return trades
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset with id {asset_id} not found."
        )


@router.get("/trades/{trade_id}", response_model=TradeSchema)
async def get_trade(trade_id: int):
    """Get a specific trade by its ID."""
    try:
        trade = await Trade.get(id=trade_id)
        return trade
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Trade with id {trade_id} not found."
        )


@router.put("/trades/{trade_id}", response_model=TradeSchema)
async def update_trade(trade_id: int, trade: TradeBase):
    """Update the details of a specific trade."""
    try:
        trade_obj = await Trade.get(id=trade_id)
        update_data = trade.model_dump(exclude_unset=True)
        await trade_obj.update_from_dict(update_data).save()
        return trade_obj
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Trade with id {trade_id} not found."
        )


@router.delete("/trades/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trade(trade_id: int):
    """Delete a specific trade."""
    try:
        trade = await Trade.get(id=trade_id)
        await trade.delete()
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Trade with id {trade_id} not found."
        )
