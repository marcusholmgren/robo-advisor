from app.models import RiskProfile
from app.schemas.risk_profile import RiskProfileCreate


async def create_risk_profile(risk_profile: RiskProfileCreate) -> RiskProfile:
    """
    Creates a new risk profile for a given portfolio.

    TODO: Implement a more complex risk assessment algorithm.
    """
    risk_profile_obj = await RiskProfile.create(**risk_profile.model_dump())
    return risk_profile_obj
