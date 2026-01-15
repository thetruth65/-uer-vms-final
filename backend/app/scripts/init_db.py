# backend/app/scripts/init_db.py
"""Initialize database with tables"""
from app.database.base import Base, engine, blockchain_engine

def init_db():
    """Create all tables"""
    print("Creating state database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ State database tables created")
    
    print("Creating blockchain database tables...")
    Base.metadata.create_all(bind=blockchain_engine)
    print("✅ Blockchain database tables created")

if __name__ == "__main__":
    init_db()