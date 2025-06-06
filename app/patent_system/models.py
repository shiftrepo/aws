from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Boolean, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

# Get database URL from environment variables or use default
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/postgres"
)

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Function to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define SQLAlchemy models for patent data

class Patent(Base):
    """Model for patent applications"""
    __tablename__ = "patents"
    
    id = Column(Integer, primary_key=True, index=True)
    application_number = Column(String(20), unique=True, index=True)
    application_date = Column(DateTime, nullable=True)
    publication_number = Column(String(20), nullable=True, index=True)
    publication_date = Column(DateTime, nullable=True)
    registration_number = Column(String(20), nullable=True)
    registration_date = Column(DateTime, nullable=True)
    title = Column(String(500), nullable=True)
    applicants = relationship("Applicant", back_populates="patent")
    inventors = relationship("Inventor", back_populates="patent")
    ipc_classifications = relationship("IPCClassification", back_populates="patent")
    abstract = Column(Text, nullable=True)
    claims = relationship("Claim", back_populates="patent")
    descriptions = relationship("Description", back_populates="patent")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert patent to dictionary"""
        return {
            "id": self.id,
            "application_number": self.application_number,
            "application_date": self.application_date,
            "publication_number": self.publication_number,
            "publication_date": self.publication_date,
            "registration_number": self.registration_number,
            "registration_date": self.registration_date,
            "title": self.title,
            "abstract": self.abstract,
            "applicants": [a.to_dict() for a in self.applicants],
            "inventors": [i.to_dict() for i in self.inventors],
            "ipc_classifications": [ipc.to_dict() for ipc in self.ipc_classifications],
            "claims": [c.to_dict() for c in self.claims],
        }


class Applicant(Base):
    """Model for patent applicants"""
    __tablename__ = "applicants"
    
    id = Column(Integer, primary_key=True, index=True)
    patent_id = Column(Integer, ForeignKey("patents.id", ondelete="CASCADE"), nullable=False)
    patent = relationship("Patent", back_populates="applicants")
    name = Column(String(200), nullable=False)
    address = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address
        }


class Inventor(Base):
    """Model for patent inventors"""
    __tablename__ = "inventors"
    
    id = Column(Integer, primary_key=True, index=True)
    patent_id = Column(Integer, ForeignKey("patents.id", ondelete="CASCADE"), nullable=False)
    patent = relationship("Patent", back_populates="inventors")
    name = Column(String(200), nullable=False)
    address = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address
        }


class IPCClassification(Base):
    """Model for IPC classifications"""
    __tablename__ = "ipc_classifications"
    
    id = Column(Integer, primary_key=True, index=True)
    patent_id = Column(Integer, ForeignKey("patents.id", ondelete="CASCADE"), nullable=False)
    patent = relationship("Patent", back_populates="ipc_classifications")
    code = Column(String(50), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "description": self.description
        }


class Claim(Base):
    """Model for patent claims"""
    __tablename__ = "claims"
    
    id = Column(Integer, primary_key=True, index=True)
    patent_id = Column(Integer, ForeignKey("patents.id", ondelete="CASCADE"), nullable=False)
    patent = relationship("Patent", back_populates="claims")
    claim_number = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "claim_number": self.claim_number,
            "text": self.text
        }


class Description(Base):
    """Model for patent descriptions"""
    __tablename__ = "descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    patent_id = Column(Integer, ForeignKey("patents.id", ondelete="CASCADE"), nullable=False)
    patent = relationship("Patent", back_populates="descriptions")
    section_title = Column(String(200), nullable=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "section_title": self.section_title,
            "text": self.text
        }


class EmbeddingCache(Base):
    """Model for caching embeddings"""
    __tablename__ = "embedding_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    text_hash = Column(String(64), unique=True, index=True)
    embedding = Column(Text, nullable=False)  # Store as JSON string
    model_id = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
