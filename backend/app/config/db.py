from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

load_dotenv()

DB_SERVER   = os.getenv("DB_SERVER", "localhost")
DB_PORT     = os.getenv("DB_PORT", "1433")
DB_NAME     = os.getenv("DB_NAME", "reservas")
DB_USER     = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

DATABASE_URL = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_SERVER},{DB_PORT}/{DB_NAME}"
    f"?driver=ODBC+Driver+17+for+SQL+Server"
)

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()