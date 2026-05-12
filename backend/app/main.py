import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controller import reserva_controller
from app.controller import laboratorio_controller
from fastapi import Request
from fastapi.responses import JSONResponse
from app.controller import horario_controller
from app.config.db import engine
from app.models.base import Base
import sqlalchemy

app = FastAPI(
    title="Sistema de Reservas de Laboratorios",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={"Access-Control-Allow-Origin": "http://localhost:5173"},
    )


def init_db():
    root_url = f"mssql+pymssql://sa:{os.getenv('DB_PASSWORD')}@db:1433/master"
    retries = 5
    while retries > 0:
        try:
            root_engine = sqlalchemy.create_engine(root_url)
            with root_engine.connect() as conn:
                conn.execution_options(isolation_level="AUTOCOMMIT")
                conn.execute(sqlalchemy.text(
                    "IF NOT EXISTS (SELECT name FROM sys.databases "
                    "WHERE name = 'reservas') CREATE DATABASE reservas"
                ))
            Base.metadata.create_all(bind=engine)
            print("Base de datos y tablas creadas exitosamente.")
            break
        except Exception as e:
            print(f"Base de datos no lista. Reintentando... ({retries-1} intentos)")
            time.sleep(5)
            retries -= 1


if os.getenv("APP_ENV") != "testing":
    init_db()


@app.get("/")
def root():
    return {"mensaje": "API funcionando correctamente"}


app.include_router(reserva_controller.router)
app.include_router(laboratorio_controller.router)
app.include_router(horario_controller.router)