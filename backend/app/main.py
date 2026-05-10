from fastapi import FastAPI
from app.controller import laboratorio_controller
from app.models.laboratorio import Laboratorio, RecursoLaboratorio    
from app.config.db import engine, Base, DB_PASSWORD 
import sqlalchemy
import time

app = FastAPI()

def init_db():
    
    root_url = f"mssql+pymssql://sa:{DB_PASSWORD}@db:1433/master"
    
    retries = 5
    while retries > 0:
        try:
            root_engine = sqlalchemy.create_engine(root_url)
            with root_engine.connect() as conn:
                conn.execution_options(isolation_level="AUTOCOMMIT")
                conn.execute(sqlalchemy.text("IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'reservas') CREATE DATABASE reservas"))
            
            Base.metadata.create_all(bind=engine)
            print("✅ Base de datos y tablas creadas exitosamente.")
            break 
        except Exception as e:
            print(f"⏳ Base de datos no lista aún. Reintentando en 5 segundos... (Quedan {retries-1} intentos)")
            time.sleep(5) 
            retries -= 1

init_db()

 
app.include_router(laboratorio_controller.router) 

@app.get("/")
def read_root():
    return {"message": "API de Reservas funcionando"}