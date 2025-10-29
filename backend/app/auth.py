
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt

from .database import get_db, Base, engine
from .models import User
from .schemas import UserCreate, LoginIn, Token
from .config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

@router.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(pw_plain: str, pw_hash: str) -> bool:
    return pwd_context.verify(pw_plain, pw_hash)

def create_access_token(subject: str, expires_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES):
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

@router.post("/signup", response_model=Token)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=payload.email, pw_hash=hash_password(payload.password), role=payload.role)
    db.add(user)
    db.commit()
    token = create_access_token(str(user.id))
    return Token(access_token=token)

@router.post("/login", response_model=Token)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.pw_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(str(user.id))
    return Token(access_token=token)
