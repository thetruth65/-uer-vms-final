from sqlalchemy import create_engine, Column, String, text, Index
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FaceEncoding(Base):
    __tablename__ = "face_encodings"
    
    voter_id = Column(String, primary_key=True, index=True)
    # DeepFace Facenet512 uses 512 dimensions
    embedding = Column(Vector(512))
    metadata_json = Column(JSONB)

# Create HNSW Index for O(log N) ANN searches
Index(
    'hnsw_index_for_face_encodings', 
    FaceEncoding.embedding, 
    postgresql_using='hnsw', 
    postgresql_with={'m': 16, 'ef_construction': 64}, 
    postgresql_ops={'embedding': 'vector_cosine_ops'}
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

# Create extension safely on startup
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()
