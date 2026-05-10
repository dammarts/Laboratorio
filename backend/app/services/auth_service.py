import os
import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import jwt

from app.models.usuario import Usuario
from app.schemas.usuario_schema import UsuarioCreate, TokenResponse
import app.repositories.usuario_repository as usuario_repo


JWT_SECRET    = os.getenv("JWT_SECRET", "dev-secret")
_ALGORITHM    = "HS256"
_EXPIRA_HORAS = 8

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def crear_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(hours=_EXPIRA_HORAS)
    return jwt.encode(payload, JWT_SECRET, algorithm=_ALGORITHM)


def login(db: Session, email: str, password: str) -> TokenResponse:
    usuario = usuario_repo.obtener_por_email(db, email)
    if not usuario or not verify_password(password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo",
        )
    token = crear_access_token({
        "sub":   usuario.usuario_id,
        "email": usuario.email,
        "rol":   usuario.rol,
    })
    return TokenResponse(access_token=token)


def registrar(db: Session, data: UsuarioCreate) -> Usuario:
    if usuario_repo.obtener_por_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese email",
        )
    nuevo = Usuario(
        email=data.email,
        password_hash=hash_password(data.password),
        rol=data.rol,
    )
    return usuario_repo.crear(db, nuevo)
