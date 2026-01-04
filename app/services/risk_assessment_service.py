"""
/home/marcus/code/marcus/robo-advisor/app/services/risk_assessment_service.py
Service for risk assessment operations.
This file handles the creation and management of user risk profiles.
RELEVANT FILES: app/models.py, app/schemas/risk_profile.py, app/routes.py
"""

from app.models import RiskProfile
from app.schemas.risk_profile import RiskProfileCreate


async def create_risk_profile(risk_profile: RiskProfileCreate) -> RiskProfile:
    """
    Creates a new risk profile for a given portfolio.

    TODO: Implement a more complex risk assessment algorithm.
    """
    risk_profile_obj = await RiskProfile.create(**risk_profile.model_dump())
    return risk_profile_obj
