from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes import auth
from app.routes import funds
from app.routes import portfolio
from sqlmodel import SQLModel
from app.db.session import async_engine
from app.services.scheduler import start_scheduler
import logging
from app.models.user import User
from app.models.fund import Fund
from app.models.portfolio import Portfolio


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI()


app.include_router(auth.router)
app.include_router(funds.router)
app.include_router(portfolio.router)

start_scheduler()

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
