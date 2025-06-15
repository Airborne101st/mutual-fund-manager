from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Portfolio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    fund_id: int = Field(foreign_key="fund.id")
    units: float
    invested_amount: float
    current_value: float = 0.0