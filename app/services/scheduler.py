from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select
from app.db.session import engine
from app.models.fund import Fund
from app.services.rapidapi_client import get_fund_details_by_fund_code
import logging

_logger = logging.getLogger(__name__)


def update_fund_navs():
    _logger.info("Starting NAV update for all mutual funds.")

    with Session(engine) as session:
        funds = session.exec(select(Fund)).all()

        if not funds:
            _logger.info("No funds found in database.")
            return

        fund_codes = ",".join([fund.fund_code for fund in funds if fund.fund_code])
        if not fund_codes:
            _logger.warning("No valid fund codes to update.")
            return

        try:
            latest_fund_details_list = get_fund_details_by_fund_code(fund_codes)
        except Exception as e:
            _logger.error(f"Failed to fetch NAVs from API: {e}")
            return

        if not latest_fund_details_list or not isinstance(latest_fund_details_list, list):
            _logger.warning("Received empty or invalid response from NAV API.")
            return

        updated_count = 0
        for fund_data in latest_fund_details_list:
            fund_code = str(fund_data.get("Scheme_Code"))
            latest_nav = fund_data.get("Net_Asset_Value")

            if not fund_code or not latest_nav:
                _logger.warning(f"Incomplete data received for fund: {fund_data}")
                continue

            fund = session.exec(select(Fund).where(Fund.fund_code == fund_code)).first()
            if not fund:
                _logger.warning(f"Fund with code {fund_code} not found in DB.")
                continue

            try:
                fund.latest_nav = float(latest_nav)
                session.add(fund)
                session.commit()
                updated_count += 1
                _logger.info(f"NAV updated for fund {fund.fund_name} ({fund_code}).")
            except Exception as e:
                _logger.error(f"Error updating fund {fund_code}: {e}")
                session.rollback()

    _logger.info(f"NAV update completed. {updated_count} fund(s) updated.")


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_fund_navs, "interval", days=1)
    scheduler.start()