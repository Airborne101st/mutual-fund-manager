from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.portfolio import Portfolio
from app.models.user import User
from app.models.fund import Fund
from app.db.session import get_session
from app.services.rapidapi_client import get_fund_details_by_fund_code
from fastapi import HTTPException, status
from app.schemas.portfolio import FundPurchase

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

@router.get("/{user_id}")
async def get_portfolio_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    statement = (
        select(Fund.fund_name, Fund.fund_family, Portfolio.units, Fund.latest_nav, Portfolio.amount)
        .join(Fund)
        .where(Portfolio.user_id == user_id)
    )
    result = await session.exec(statement)
    portfolio_records = result.all()

    if not portfolio_records:
        return {
            "Current_Portfolio_Value": 0,
            "Portfolio_Details": [],
            "message": "No portfolio found for this user"
        }

    portfolio_details = []
    total_value = 0
    for fund_name, fund_family, units, latest_nav, amount in portfolio_records:
        portfolio_details.append({
            "Fund_Name": fund_name,
            "Fund_Family_Name": fund_family,
            "Total_Units": units,
            "Current_Value": amount
        })
        total_value += amount

    return {
        "Current_Portfolio_Value": round(total_value, 2),
        "Portfolio_Details": portfolio_details
    }

@router.post("/buy-fund")
async def post_fund_units_in_portfolio(purchase: FundPurchase, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, purchase.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check for existing fund in portfolio
    statement = (
        select(Portfolio)
        .join(Fund)
        .join(User)
        .where(Fund.fund_code == purchase.fund_code)
        .where(User.id == purchase.user_id)
    )
    result = await session.exec(statement)
    existing_fund_in_portfolio = result.first()

    if existing_fund_in_portfolio:
        fund = await session.get(Fund, existing_fund_in_portfolio.fund_id)
        new_units_added = purchase.amount/fund.latest_nav
        existing_fund_in_portfolio.units += new_units_added
        existing_fund_in_portfolio.amount = existing_fund_in_portfolio.units * fund.latest_nav
        session.add(existing_fund_in_portfolio)
        await session.commit()
        return {"message": f"Updated {new_units_added} units in {fund.fund_name}"}

    # Check if fund already exists
    result = await session.exec(select(Fund).where(Fund.fund_code == purchase.fund_code))
    existing_fund = result.first()

    if existing_fund:
        new_portfolio_fund = Portfolio(user_id=purchase.user_id, fund_id=existing_fund.id, amount=purchase.amount)
        new_portfolio_fund.units = purchase.amount / existing_fund.latest_nav
        session.add(new_portfolio_fund)
        await session.commit()
        return {"message": f"Added {new_portfolio_fund.units} units to {existing_fund.fund_name}"}

    # Fetch from RapidAPI
    try:
        new_fund_details = await get_fund_details_by_fund_code(purchase.fund_code)
        if not new_fund_details or not isinstance(new_fund_details, list):
            raise ValueError("Invalid response from fund API")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Unable to fetch fund data: {e}")

    fund_info = new_fund_details[0]
    fund_name = fund_info.get("Scheme_Name")
    fund_family = fund_info.get("Mutual_Fund_Family")
    latest_nav = float(fund_info.get("Net_Asset_Value", 0))

    # Create new fund
    new_fund = Fund(
        fund_code=purchase.fund_code,
        fund_name=fund_name,
        fund_family=fund_family,
        latest_nav=latest_nav
    )
    session.add(new_fund)
    await session.commit()
    await session.refresh(new_fund)

    # Create new portfolio record
    new_portfolio_fund = Portfolio(user_id=purchase.user_id, fund_id=new_fund.id, amount=purchase.amount)
    new_portfolio_fund.units = new_portfolio_fund.amount / new_fund.latest_nav
    session.add(new_portfolio_fund)
    await session.commit()

    return {"message": f"Added {new_portfolio_fund.units} units to {fund_name}"}
