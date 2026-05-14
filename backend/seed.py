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
    from app.models import Base, Usuario, Laboratorio  # noqa: F401 — registra todos los modelos
    from app.services.auth_service import hash_password

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existente = db.query(Usuario).filter(Usuario.email == email).first()
        if existente:
            print(f"INFO: El usuario '{email}' ya existe (id={existente.usuario_id}). Sin cambios.")
        else:

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
        email_docente = "jp@universidad.edu"
        existente_doc = db.query(Usuario).filter(Usuario.email == email_docente).first()
        if not existente_doc:
            docente = Usuario(
                email=email_docente,
                password_hash=hash_password("test1234"),
                rol="DOCENTE",
                activo=True,
            )
            db.add(docente)
            db.commit()
            print(f"OK: Usuario DOCENTE '{email_docente}' creado.")

        # Crear laboratorio de prueba (ID=1) para que Locust no dé 404 Not Found
        existente_lab = db.query(Laboratorio).filter(Laboratorio.laboratorio_id == 1).first()
        if not existente_lab:
            lab = Laboratorio(
                laboratorio_id=1,
                nombre="Laboratorio de Sistemas (Prueba Locust)",
                ubicacion="Bloque C - Piso 1",
                capacidad_maxima=40,
                tipo_laboratorio="COMPUTO",
                estado=True
            )
            db.add(lab)
            db.commit()
            print("OK: Laboratorio de prueba (ID=1) creado exitosamente.")

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
