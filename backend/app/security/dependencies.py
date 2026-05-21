from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.config.db import get_db
from app.security.config import JWT_SECRET, ALGORITHM
import app.repositories.usuario_repository as usuario_repo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


@dataclass
class UsuarioActual:
    """Usuario autenticado en la request actual."""
    usuario_id: int
    email:      str
    rol:        str  # "ADMIN", "COORDINADOR", "DOCENTE", "CONSULTA"


def get_current_user(
    token: str     = Depends(oauth2_scheme),
    db:    Session = Depends(get_db),
) -> UsuarioActual:
    error_401 = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado o token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise error_401
    try:
        payload    = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        usuario_id = payload.get("sub")
        if usuario_id is None:
            raise error_401
    except JWTError:
        raise error_401

    usuario = usuario_repo.obtener_por_id(db, int(usuario_id))
    if not usuario or not usuario.activo:
        raise error_401

    return UsuarioActual(
        usuario_id=usuario.usuario_id,
        email=usuario.email,
        rol=usuario.rol,
    )


def require_roles(*roles_permitidos: str):
    """
    Dependencia parametrizada para exigir rol específico.

    USO:
        @router.post("/reservas",
                     dependencies=[Depends(require_roles("ADMIN", "DOCENTE"))])
    """
    def role_checker(usuario: UsuarioActual = Depends(get_current_user)) -> UsuarioActual:
        if usuario.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol {usuario.rol} insuficiente. Requeridos: {roles_permitidos}",
            )
        return usuario
    return role_checker


todos_autenticados = Depends(get_current_user)
