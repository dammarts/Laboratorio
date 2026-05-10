import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

DB_SERVER   = "db"
DB_NAME     = "reservas"
DB_USER     = "sa"
DB_PASSWORD = os.getenv("DB_PASSWORD") 

DATABASE_URL = f"mssql+pymssql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:1433/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. Función para FastAPI
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_connection():
    import pymssql
    return pymssql.connect(server=DB_SERVER, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)