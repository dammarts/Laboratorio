from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.usuario import Usuario


def obtener_por_email(db: Session, email: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.email == email).first()


def obtener_por_id(db: Session, usuario_id: int) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.usuario_id == usuario_id).first()


def crear(db: Session, usuario: Usuario) -> Usuario:
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def listar(db: Session) -> List[Usuario]:
    return db.query(Usuario).all()
