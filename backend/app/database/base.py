# backend/app/database/base.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# State Database Engine
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

# Blockchain Database Engine
blockchain_engine = create_engine(settings.BLOCKCHAIN_URL, pool_pre_ping=True)
BlockchainSessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=blockchain_engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_blockchain_db():
    db = BlockchainSessionLocal()
    try:
        yield db
    finally:
        db.close()