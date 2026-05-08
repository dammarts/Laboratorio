from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import os
from dotenv import load_dotenv

load_dotenv()

DB_SERVER   = os.getenv("DB_SERVER", "db")
DB_PORT     = os.getenv("DB_PORT", "1433")
DB_NAME     = os.getenv("DB_NAME", "reservas")
DB_USER     = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Admin1234!")

# AQUÍ ESTÁ LA MAGIA: Usamos pymssql
DATABASE_URL = f"mssql+pymssql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_connection():
    import pymssql
    return pymssql.connect(
        server=DB_SERVER,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )