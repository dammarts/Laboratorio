# backend/app/security/dependencies.py
from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


@dataclass
class UsuarioActual:
    """Usuario autenticado en la request actual."""
    usuario_id: int
    email: str
    rol: str  # "ADMIN", "COORDINADOR", "DOCENTE", "CONSULTA"


def get_current_user(token: str = Depends(oauth2_scheme)) -> UsuarioActual:
    """
    STUB temporal hasta que se implemente auth real.
    
    Cuando se implemente la rama feature/auth:
    - Decodificar JWT del token
    - Buscar usuario en BD
    - Retornar UsuarioActual con datos reales
    
    La firma NO cambia. Los módulos que usan Depends(get_current_user)
    no necesitan modificarse.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )
    # STUB: cualquier token no vacío retorna admin dummy
    return UsuarioActual(
        usuario_id=1,
        email="admin@stub.local",
        rol="ADMIN",
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
                detail=f"Rol {usuario.rol} insuficiente. Requeridos: {roles_permitidos}"
            )
        return usuario
    return role_checker


todos_autenticados = Depends(get_current_user)