from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.fund import Fund
from app.db.session import get_session
from app.schemas.portfolio import FundPurchase
import app.services.portfolio_service as ps

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/{user_id}")
async def get_portfolio_user(user_id: int, session: AsyncSession = Depends(get_session)):
    await ps.get_user(session, user_id)
    portfolio_records = await ps.fetch_user_portfolio(session, user_id)
    return ps.build_portfolio_summary(portfolio_records)


@router.post("/buy-fund")
async def post_funds_in_portfolio(purchase: FundPurchase, session: AsyncSession = Depends(get_session)):
    await ps.get_user(session, purchase.user_id)

    existing_portfolio = await ps.get_portfolio_fund(session, purchase.user_id, purchase.fund_code)
    if existing_portfolio:
        fund = await session.get(Fund, existing_portfolio.fund_id)
        message = await ps.update_existing_portfolio(session, existing_portfolio, fund, purchase.amount)
        return {"message": message}

    fund = await ps.get_existing_fund(session, purchase.fund_code)
    if not fund:
        fund = await ps.create_fund_from_api(session, purchase.fund_code)

    message = await ps.add_to_portfolio(session, purchase.user_id, fund, purchase.amount)
    return {"message": message}
