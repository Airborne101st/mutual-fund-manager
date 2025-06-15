from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.models.portfolio import Portfolio
from app.models.user import User
from app.models.fund import Fund
from app.db.session import get_session
from app.services.rapidapi_client import get_fund_details_by_fund_code

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

@router.get("/{user_id}")
def get_portfolio_user(user_id: int, session: Session = Depends(get_session)):
    latest_portfolio_details = {
        "Current_Portfolio_Value": 0,
        "Portfolio_Details": False
    }
    portfolio_records = session.exec(select(Fund.fund_name, Fund.fund_family, Portfolio.units, Fund.latest_nav).join(Fund).where(Portfolio.user_id == user_id)).all()
    portfolio_details = []
    total_value = 0
    for portfolio_record in portfolio_records:
        fund_name = portfolio_record[0]
        fund_family_name = portfolio_record[1]
        total_units = portfolio_record[2]
        latest_nav = portfolio_record[3]

        current_value = total_units * latest_nav
        portfolio_dict = {
            "Fund_Name": fund_name,
            "Fund_Family_Name": fund_family_name,
            "Total_Units": total_units,
            "Current_Value":  current_value
        }
        portfolio_details.append(portfolio_dict)
        total_value += current_value

    latest_portfolio_details.update({
        "Current_Portfolio_Value": total_value,
        "Portfolio_Details": portfolio_details
    })
    return latest_portfolio_details

@router.post("/buy-fund/{fund_code}/units/{units}/user/{user_id}")
def post_fund_units_in_portfolio(fund_code: str, units: int, user_id: int, session: Session = Depends(get_session)):
    statement = select(Portfolio).join(Fund).join(User).where(Fund.fund_code == fund_code).where(User.id == user_id)
    existing_fund = session.exec(statement).first()
    if existing_fund:
        # Update units if fund already exists
        existing_fund.units += units
        session.commit()
        fund = session.get(Fund, existing_fund.fund_id)
        return {"message": f"Added {units} units to {fund.fund_name}"}

    # Create a new Fund and add in portfolio
    new_fund_details = get_fund_details_by_fund_code(fund_code)
    if new_fund_details:
        fund_dict = dict(new_fund_details[0])
        fund_name = fund_dict.get("Scheme_Name")
        fund_family = fund_dict.get("Mutual_Fund_Family")
        latest_nav = fund_dict.get("Net_Asset_Value")

        new_fund = Fund(fund_code=fund_code, fund_name=fund_name, fund_family=fund_family, latest_nav=latest_nav)
        session.add(new_fund)
        session.commit()
        session.refresh(new_fund)

        new_fund_id = new_fund.id

        new_portfolio_fund = Portfolio(user_id=user_id, fund_id=new_fund_id, units=units)
        session.add(new_portfolio_fund)
        session.commit()
        return {"message": f"Added {units} units to {new_fund.fund_name}"}




