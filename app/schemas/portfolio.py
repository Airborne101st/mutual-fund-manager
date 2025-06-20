from pydantic import BaseModel, Field

class FundPurchase(BaseModel):
    fund_code: str = Field(..., example="102345")
    amount: float = Field(..., gt=0, example=1000.0)
    user_id: int = Field(..., gt=0, example=1)
