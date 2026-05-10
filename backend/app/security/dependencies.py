from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    # Versión simplificada hasta que auth esté implementado
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )
    return {"token": token}


def require_roles(*roles: str):
    def role_checker(current_user=Depends(get_current_user)):
        return current_user
    return role_checker


todos_autenticados = Depends(get_current_user)