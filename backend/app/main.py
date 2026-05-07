from fastapi import FastAPI
from app.controller import reserva_controller
from app.controller import laboratorio_controller

app = FastAPI()

app.include_router(reserva_controller.router) 