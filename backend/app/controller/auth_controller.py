from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.db import get_db
from app.security.dependencies import get_current_user, require_roles, UsuarioActual
from app.schemas.usuario_schema import UsuarioCreate, UsuarioResponse, LoginRequest, TokenResponse
import app.services.auth_service as auth_service
import app.repositories.usuario_repository as usuario_repo

router_auth     = APIRouter(prefix="/auth",     tags=["auth"])
router_usuarios = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router_auth.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, data.email, data.password)


@router_auth.post(
    "/register",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("ADMIN"))],
)
def registrar(data: UsuarioCreate, db: Session = Depends(get_db)):
    return auth_service.registrar(db, data)


@router_usuarios.get(
    "/",
    response_model=List[UsuarioResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("ADMIN"))],
)
def listar_usuarios(db: Session = Depends(get_db)):
    return usuario_repo.listar(db)


@router_usuarios.get(
    "/me",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
)
def perfil(
    usuario: UsuarioActual = Depends(get_current_user),
    db:      Session       = Depends(get_db),
):
    return usuario_repo.obtener_por_id(db, usuario.usuario_id)
