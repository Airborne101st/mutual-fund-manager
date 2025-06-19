from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.user import User
from app.db.session import get_session
from app.utils.security import hash_password, verify_password
from app.schemas.auth import AuthRequest

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(data: AuthRequest, session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(User).where(User.email == data.email))
    existing_user = result.first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=data.email, password_hash=hash_password(data.password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {"message": "User registered", "user_id": user.id}

@router.post("/login")
async def login(data: AuthRequest, session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(User).where(User.email == data.email))
    user = result.first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": user.id}