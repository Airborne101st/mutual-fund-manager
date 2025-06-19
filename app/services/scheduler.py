from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.session import async_session
from sqlmodel import select
from apscheduler.triggers.interval import IntervalTrigger
from app.models.fund import Fund
from app.services.rapidapi_client import get_fund_details_by_fund_code
import logging

_logger = logging.getLogger(__name__)


async def update_fund_navs():
    _logger.info("Starting NAV update for all mutual funds.")

    async with async_session() as session:
        result = await session.exec(select(Fund))
        funds = result.all()

        if not funds:
            _logger.info("No funds found in database.")
            return

        fund_codes = ",".join([fund.fund_code for fund in funds if fund.fund_code])
        if not fund_codes:
            _logger.warning("No valid fund codes to update.")
            return

        try:
            latest_fund_details_list = await get_fund_details_by_fund_code(fund_codes)
        except Exception as e:
            _logger.error(f"Failed to fetch NAVs from API: {e}")
            return

        updated_count = 0
        for fund_data in latest_fund_details_list:
            fund_code = str(fund_data.get("Scheme_Code"))
            latest_nav = fund_data.get("Net_Asset_Value")

            if not fund_code or not latest_nav:
                _logger.warning(f"Incomplete data for fund: {fund_data}")
                continue

            result = await session.exec(select(Fund).where(Fund.fund_code == fund_code))
            fund = result.first()
            if not fund:
                _logger.warning(f"Fund {fund_code} not found.")
                continue

            try:
                fund.latest_nav = float(latest_nav)
                session.add(fund)
                await session.commit()
                _logger.info(f"NAV updated for {fund.fund_name} ({fund_code})")
                updated_count += 1
            except Exception as e:
                _logger.error(f"Error updating {fund_code}: {e}")
                await session.rollback()

    _logger.info(f"NAV update completed. {updated_count} funds updated.")


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_fund_navs, IntervalTrigger(days=1))
    scheduler.start()
    _logger.info("Scheduler started.")