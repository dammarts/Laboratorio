import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controller import reserva_controller
from app.controller import laboratorio_controller
from fastapi import Request
from fastapi.responses import JSONResponse
from app.controller import horario_controller
from app.controller import auth_controller
from app.controller import reporte_controller
from app.config.db import engine
from app.models.base import Base

app = FastAPI(
    title="Sistema de Reservas de Laboratorios",
    version="1.0.0"
)

CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={"Access-Control-Allow-Origin": CORS_ORIGIN},
    )


def init_db():
    retries = 5
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            print("Base de datos y tablas creadas exitosamente.")
            break
        except Exception as e:
            print(f"⚠️ ERROR REAL DE CONEXIÓN: {e}")
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
app.include_router(auth_controller.router_auth)
app.include_router(auth_controller.router_usuarios)
app.include_router(reporte_controller.router)
