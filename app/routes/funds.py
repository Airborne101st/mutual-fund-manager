from fastapi import APIRouter
from app.services.rapidapi_client import get_funds_by_family
from app.services.rapidapi_client import get_fund_details_by_fund_code
from fastapi import HTTPException
from typing import Any

router = APIRouter(prefix="/funds", tags=["funds"])

@router.get("/family/{family}", response_model=Any)
def get_mutual_funds_by_family(family: str):
    try:
        return get_funds_by_family(family)
    except HTTPException as e:
        raise e


@router.get("/code/{fund_code}", response_model=Any)
def get_mutual_fund_details_by_fund_code(fund_code: str):
    try:
        return get_fund_details_by_fund_code(fund_code)
    except HTTPException as e:
        raise e
