import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

# HARDCODED FOR DEPLOYMENT - External URL
DATABASE_URL = "postgresql://stocksense_user:FrprtpviOU7BqVBXQBL8xK75vdiKuQWh@dpg-db4gm0e0tbbc73eathlg-a.singapore-postgres.render.com:5432/stocksense_5vus"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Engine with SSL configuration for Render
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "prefer", "connect_timeout": 30},
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()