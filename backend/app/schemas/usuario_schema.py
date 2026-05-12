import datetime
from pydantic import BaseModel, Field, validator


_ROLES_VALIDOS = {"ADMIN", "COORDINADOR", "DOCENTE", "CONSULTA"}


class UsuarioCreate(BaseModel):
    email:    str = Field(..., min_length=5,  max_length=150)
    password: str = Field(..., min_length=8,  max_length=100)
    rol:      str = Field(..., max_length=20)

    @validator("rol")
    def rol_valido(cls, v: str) -> str:
        if v not in _ROLES_VALIDOS:
            raise ValueError(f"Rol inválido. Opciones: {sorted(_ROLES_VALIDOS)}")
        return v


class UsuarioResponse(BaseModel):
    usuario_id: int
    email:      str
    rol:        str
    activo:     bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email:    str = Field(..., min_length=5, max_length=150)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
