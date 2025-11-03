"""Database models using TortoiseORM."""

from tortoise import fields
from tortoise.models import Model


class Portfolio(Model):
    """Portfolio model representing an investment portfolio."""
    
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "portfolios"

    def __str__(self):
        return self.name


class Asset(Model):
    """Asset model representing a financial asset in a portfolio."""
    
    id = fields.IntField(primary_key=True)
    portfolio = fields.ForeignKeyField("models.Portfolio", related_name="assets")
    symbol = fields.CharField(max_length=20)
    name = fields.CharField(max_length=255)
    quantity = fields.DecimalField(max_digits=20, decimal_places=8, default=0)
    purchase_price = fields.DecimalField(max_digits=20, decimal_places=2, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "assets"

    def __str__(self):
        return f"{self.symbol} - {self.name}"


class RiskProfile(Model):
    """Risk profile model representing the user's risk tolerance."""

    id = fields.IntField(primary_key=True)
    portfolio = fields.OneToOneField("models.Portfolio", related_name="risk_profile")
    risk_score = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "risk_profiles"

    def __str__(self):
        return f"Risk profile for portfolio {self.portfolio.name}"
