from fastapi import APIRouter
from app.services.rapidapi_client import get_funds_by_family
from app.services.rapidapi_client import get_fund_details_by_fund_code

router = APIRouter(prefix="/funds", tags=["funds"])

@router.get("/family/{family}")
def get_mutual_funds_by_family(family: str):
    return get_funds_by_family(family)

@router.get("/code/{fund_code}")
def get_mutual_fund_details_by_fund_code(fund_code: str):
    return get_fund_details_by_fund_code(fund_code)



