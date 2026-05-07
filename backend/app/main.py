from fastapi import FastAPI
from app.controller import horario_controller

app = FastAPI(
    title="Sistema de Reservas de Laboratorios",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"mensaje": "API funcionando correctamente"}

app.include_router(horario_controller.router)