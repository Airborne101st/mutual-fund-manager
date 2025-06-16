from pydantic import BaseModel, Field

class FundPurchase(BaseModel):
    fund_code: str = Field(..., example="102345")
    units: int = Field(..., gt=0, example=10)
    user_id: int = Field(..., gt=0, example=1)
