from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select
from app.db.session import engine
from app.models.fund import Fund
from app.services.rapidapi_client import get_fund_details_by_fund_code
import logging

_logger = logging.getLogger(__name__)


def update_fund_navs():
    _logger.info("Updating Mutual Fund NAVs")
    with Session(engine) as session:
        funds = session.exec(select(Fund)).all()
        fund_codes = ''
        for fund in funds:
            fund_codes += f',{fund.fund_code}'
        fund_codes = fund_codes.lstrip(',')

        latest_fund_details_list = get_fund_details_by_fund_code(fund_codes)

        if latest_fund_details_list:
            for latest_fund_details in latest_fund_details_list:
                fund_code = str(latest_fund_details.get("Scheme_Code"))
                fund = session.exec(select(Fund).where(Fund.fund_code == fund_code)).first()
                fund.latest_nav = latest_fund_details.get("Net_Asset_Value")
                _logger.info("NAV Updated")
                session.commit()
    _logger.info("Mutual Fund NAVs Updated")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_fund_navs, "interval", days=1)
    scheduler.start()
    _logger.info("Starting Scheduler to update Fund NAVs:")