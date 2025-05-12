# app/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, config
from app.database import SessionLocal
from app.models import User
from app.dependencies import get_current_user
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from typing import Generator

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Obtiene la sesión de base de datos

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Lógica para decodificar el token y obtener el usuario actual

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# Control de Rol

def require_role(role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user