"""
/home/marcus/code/marcus/robo-advisor/app/schemas/risk_profile.py
Pydantic schemas for risk profile validation.
This file defines the data structures for creating and retrieving risk profiles.
RELEVANT FILES: app/models.py, app/routes.py, app/services/risk_assessment_service.py
"""

from pydantic import BaseModel, ConfigDict


class RiskProfileBase(BaseModel):
    """Base risk profile schema."""
    risk_score: int


class RiskProfileCreate(RiskProfileBase):
    """Schema for creating a risk profile."""
    portfolio_id: int


class RiskProfile(RiskProfileBase):
    """Schema for risk profile response."""
    id: int

    model_config = ConfigDict(from_attributes=True)
