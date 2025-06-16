from fastapi import FastAPI
from app.routes import auth
from app.routes import funds
from app.routes import portfolio
from sqlmodel import SQLModel
from app.db.session import engine
from app.services.scheduler import start_scheduler
import logging
from app.models.user import User
from app.models.fund import Fund
from app.models.portfolio import Portfolio


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = FastAPI()

SQLModel.metadata.create_all(engine)

app.include_router(auth.router)
app.include_router(funds.router)
app.include_router(portfolio.router)

start_scheduler()
