import os
import sys

from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    email    = os.getenv("SEED_EMAIL")
    password = os.getenv("SEED_PASSWORD")

    if not email or not password:
        print("ERROR: SEED_EMAIL y SEED_PASSWORD son obligatorias.")
        sys.exit(1)

    from app.config.db import SessionLocal, engine
    from app.models import Base, Usuario  # noqa: F401 — registra todos los modelos
    from app.services.auth_service import hash_password

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existente = db.query(Usuario).filter(Usuario.email == email).first()
        if existente:
            print(f"INFO: El usuario '{email}' ya existe (id={existente.usuario_id}). Sin cambios.")
            return

        admin = Usuario(
            email=email,
            password_hash=hash_password(password),
            rol="ADMIN",
            activo=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"OK: Usuario ADMIN '{email}' creado con id={admin.usuario_id}.")

        # Crear docente para pruebas de carga
        email_docente = "docente@universidad.edu"
        existente_doc = db.query(Usuario).filter(Usuario.email == email_docente).first()
        if not existente_doc:
            docente = Usuario(
                email=email_docente,
                password_hash=hash_password("Docente123!"),
                rol="DOCENTE",
                activo=True,
            )
            db.add(docente)
            db.commit()
            print(f"OK: Usuario DOCENTE '{email_docente}' creado.")

    except Exception as exc:
        db.rollback()
        print(f"ERROR: {exc}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()


# Uso:
# SEED_EMAIL=admin@uni.edu SEED_PASSWORD=Admin123! python seed.py
#
# En Windows (PowerShell):
# $env:SEED_EMAIL="admin@uni.edu"; $env:SEED_PASSWORD="Admin123!"; python seed.py
#
# Requisitos previos: la BD debe estar corriendo y las variables de entorno
# DB_USER, DB_PASSWORD, DB_NAME configuradas (o DATABASE_URL completa).
