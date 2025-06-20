from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.portfolio import Portfolio
from app.models.user import User
from app.models.fund import Fund
from fastapi import HTTPException, status
from sqlmodel import select
from app.services.rapidapi_client import get_fund_details_by_fund_code

async def get_user(session: AsyncSession, user_id: int) -> User:
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def get_portfolio_fund(session: AsyncSession, user_id: int, fund_code: str) -> Portfolio | None:
    statement = (
        select(Portfolio)
        .join(Fund)
        .join(User)
        .where(Fund.fund_code == fund_code)
        .where(User.id == user_id)
    )
    result = await session.exec(statement)
    return result.first()


async def get_existing_fund(session: AsyncSession, fund_code: str) -> Fund | None:
    result = await session.exec(select(Fund).where(Fund.fund_code == fund_code))
    return result.first()


async def create_fund_from_api(session: AsyncSession, fund_code: str) -> Fund:
    try:
        fund_details = await get_fund_details_by_fund_code(fund_code)
        if not fund_details or not isinstance(fund_details, list):
            raise ValueError("Invalid response from fund API")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Unable to fetch fund data: {e}")

    data = fund_details[0]
    fund = Fund(
        fund_code=fund_code,
        fund_name=data.get("Scheme_Name"),
        fund_family=data.get("Mutual_Fund_Family"),
        latest_nav=float(data.get("Net_Asset_Value", 0))
    )
    session.add(fund)
    await session.commit()
    await session.refresh(fund)
    return fund


async def update_existing_portfolio(
    session: AsyncSession, portfolio: Portfolio, fund: Fund, amount: float
) -> str:
    new_units = amount / fund.latest_nav
    portfolio.units += new_units
    portfolio.amount = portfolio.units * fund.latest_nav
    session.add(portfolio)
    await session.commit()
    return f"Added {new_units} units in {fund.fund_name}"


async def add_to_portfolio(
    session: AsyncSession, user_id: int, fund: Fund, amount: float
) -> str:
    units = amount / fund.latest_nav
    portfolio = Portfolio(user_id=user_id, fund_id=fund.id, units=units, amount=amount)
    session.add(portfolio)
    await session.commit()
    return f"Added {units} units to {fund.fund_name}"


async def fetch_user_portfolio(session: AsyncSession, user_id: int):
    statement = (
        select(Fund.fund_name, Fund.fund_family, Portfolio.units, Fund.latest_nav, Portfolio.amount)
        .join(Fund)
        .where(Portfolio.user_id == user_id)
    )
    result = await session.exec(statement)
    return result.all()


def build_portfolio_summary(portfolio_records: list[tuple]) -> dict:
    if not portfolio_records:
        return {
            "Current_Portfolio_Value": 0,
            "Portfolio_Details": [],
            "message": "No portfolio found for this user"
        }

    total_value = 0
    details = []

    for fund_name, fund_family, units, latest_nav, amount in portfolio_records:
        details.append({
            "Fund_Name": fund_name,
            "Fund_Family_Name": fund_family,
            "Total_Units": units,
            "Current_Value": amount
        })
        total_value += amount

    return {
        "Current_Portfolio_Value": round(total_value, 2),
        "Portfolio_Details": details
    }
