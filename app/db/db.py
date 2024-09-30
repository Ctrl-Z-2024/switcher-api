from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Conexión a la base de datos SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./switcher.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Base.metadata.create_all(bind=engine) #! TO FIX: Setting this function here doesn't define the database.

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()