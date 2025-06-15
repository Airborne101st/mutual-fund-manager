from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select
from app.db.session import engine
from app.models.fund import Fund
from app.services.rapidapi_client import get_fund_details_by_fund_code
import logging


def update_fund_navs():
    logging.info("Updating Mutual Fund NAVs")
    with Session(engine) as session:
        funds = session.exec(select(Fund)).all()
        fund_codes = ''
        for fund in funds:
            fund_codes += f',{fund.fund_code}'
        fund_codes = fund_codes.lstrip(',')
        print("fund_codes", fund_codes)
        latest_fund_details_list = get_fund_details_by_fund_code(fund_codes)
        print("latest_fund_details_list", latest_fund_details_list)
        if latest_fund_details_list:
            for latest_fund_details in latest_fund_details_list:
                fund_code = str(latest_fund_details.get("Scheme_Code"))
                fund = session.exec(select(Fund).where(Fund.fund_code == fund_code)).first()
                fund.latest_nav = latest_fund_details.get("Net_Asset_Value")
                logging.info("NAV Updated")
                session.commit()
    logging.info("Mutual Fund NAVs Updated")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_fund_navs, "interval", days=1)
    scheduler.start()
    logging.info("Starting Scheduler:")