from fastapi import FastAPI
from app.controllers import reserva_controller

app = FastAPI()

app.include_router(reserva_controller.router) 