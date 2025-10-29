from fastapi import Depends, HTTPException, APIRouter, Body, Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.database import get_db
from app.models import User, RoleEnum
from app.config import settings
from app.schemas import SignupIn, TokenOut
from app.observability.langfuse_client import lf_trace, lf_span
from passlib.context import CryptContext
import logging

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# swap bcrypt → bcrypt_sha256
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

def hash_password(pw: str) -> str:
    # no truncation needed with bcrypt_sha256
    return pwd_context.hash(pw)

def verify_password(pw: str, pw_hash: str) -> bool:
    return pwd_context.verify(pw, pw_hash)


def create_access_token(data: dict, expires_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGO)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO])
        email: str = payload.get("sub")
        if email is None:
            raise ValueError("bad sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Admins only")
    return user

@router.post("/signup", response_model=TokenOut)
def signup(payload: SignupIn = Body(...), db: Session = Depends(get_db), request: Request = None):
    with lf_trace(name="auth.signup", user_id=payload.email, metadata={"role": payload.role.value}) as trace:
        pw_hash = hash_password(payload.password)
        logging.info(payload.password)
        if db.query(User).filter(User.email == payload.email).first():
            raise HTTPException(400, "Email already in use")
        user = User(email=payload.email, password_hash=pw_hash, role=payload.role)
        db.add(user); db.commit(); db.refresh(user)
        token = create_access_token({"sub": user.email})
        return TokenOut(access_token=token)

@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    with lf_trace(name="auth.login", user_id=form.username):
        user = db.query(User).filter(User.email == form.username).first()
        ok = user and verify_password(form.password, user.password_hash)
        if not ok:
            raise HTTPException(401, "Invalid credentials")
        token = create_access_token({"sub": user.email})
        return TokenOut(access_token=token)
