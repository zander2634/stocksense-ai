import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# HARDCODED FOR DEPLOYMENT
DATABASE_URL = "postgresql://stocksense_user:FrprtpviOU7BqVBXQBL8xK75vdiKuQWh@dpg-db4gm0e0tbbc73eathlg-a.singapore-postgres.render.com:5432/stocksense_5vus?sslmode=require"

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()