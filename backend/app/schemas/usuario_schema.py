import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


_ROLES_VALIDOS = {"ADMIN", "COORDINADOR", "DOCENTE", "CONSULTA"}


class UsuarioCreate(BaseModel):
    email:    str = Field(..., min_length=5,  max_length=150)
    password: str = Field(..., min_length=8,  max_length=100)
    rol:      str = Field(..., max_length=20)

    @field_validator("rol")
    @classmethod
    def rol_valido(cls, v: str) -> str:
        if v not in _ROLES_VALIDOS:
            raise ValueError(f"Rol inválido. Opciones: {sorted(_ROLES_VALIDOS)}")
        return v


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    usuario_id: int
    email:      str
    rol:        str
    activo:     bool
    created_at: datetime.datetime


class LoginRequest(BaseModel):
    email:    str = Field(..., min_length=5, max_length=150)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
