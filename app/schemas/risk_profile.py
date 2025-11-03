from pydantic import BaseModel, ConfigDict

class RiskProfileBase(BaseModel):
    risk_score: int

class RiskProfileCreate(RiskProfileBase):
    portfolio_id: int

class RiskProfile(RiskProfileBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
