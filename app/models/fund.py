from sqlmodel import SQLModel, Field
from typing import Optional

class Fund(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fund_code: str = Field(unique=True)
    fund_name: str
    fund_family: str
    latest_nav: float