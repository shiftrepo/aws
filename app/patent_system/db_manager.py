import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from dateutil import parser as date_parser
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from app.patent_system.models import (
    Patent, Applicant, Inventor, IPCClassification,
    Claim, Description, EmbeddingCache, get_db
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PatentDBManager:
    """Class to manage patent data in the database"""
    
    def __init__(self, db_session=None):
        """Initialize with optional database session"""
        self.db = db_session
    
    def __enter__(self):
        """Context manager entry"""
        if self.db is None:
            self.db = next(get_db())
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.db is not None:
            self.db.close()
    
    def store_patent(self, patent_data: Dict[str, Any]) -> Optional[Patent]:
        """
        Store a patent and its related data in the database
        
        Args:
            patent_data: Dictionary containing patent data from J-PlatPat
            
        Returns:
            Patent object if successful, None otherwise
        """
        try:
            # Extract basic patent information
            application_number = patent_data.get("applicationNumber")
            
            # Check if patent already exists
            existing_patent = self.db.query(Patent).filter_by(
                application_number=application_number
            ).first()
            
            if existing_patent:
                logger.info(f"Patent with application number {application_number} already exists, updating")
                patent = existing_patent
            else:
                patent = Patent(
                    application_number=application_number
                )
                logger.info(f"Creating new patent with application number {application_number}")
            
            # Update patent attributes
            patent.title = patent_data.get("title")
            patent.abstract = patent_data.get("abstract")
            
            # Parse dates
            if patent_data.get("applicationDate"):
                try:
                    patent.application_date = date_parser.parse(patent_data.get("applicationDate"))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid application date format: {e}")
            
            if patent_data.get("publicationDate"):
                try:
                    patent.publication_date = date_parser.parse(patent_data.get("publicationDate"))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid publication date format: {e}")
            
            if patent_data.get("registrationDate"):
                try:
                    patent.registration_date = date_parser.parse(patent_data.get("registrationDate"))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid registration date format: {e}")
            
            patent.publication_number = patent_data.get("publicationNumber")
            patent.registration_number = patent_data.get("registrationNumber")
            
            # Save patent to get ID if it's new
            if not existing_patent:
                self.db.add(patent)
                self.db.commit()
                self.db.refresh(patent)
            
            # Process related entities
            self._process_applicants(patent, patent_data.get("applicants", []))
            self._process_inventors(patent, patent_data.get("inventors", []))
            self._process_ipc_classifications(patent, patent_data.get("ipcClassifications", []))
            self._process_claims(patent, patent_data.get("claims", []))
            self._process_descriptions(patent, patent_data.get("descriptions", []))
            
            # Commit all changes
            self.db.commit()
            return patent
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error storing patent: {str(e)}")
            return None
    
    def _process_applicants(self, patent: Patent, applicants_data: List[Dict[str, Any]]):
        """Process and store patent applicants"""
        # Remove existing applicants if updating
        if patent.id:
            self.db.query(Applicant).filter_by(patent_id=patent.id).delete()
        
        # Add new applicants
        for applicant_data in applicants_data:
            applicant = Applicant(
                patent_id=patent.id,
                name=applicant_data.get("name", ""),
                address=applicant_data.get("address", "")
            )
            self.db.add(applicant)
    
    def _process_inventors(self, patent: Patent, inventors_data: List[Dict[str, Any]]):
        """Process and store patent inventors"""
        # Remove existing inventors if updating
        if patent.id:
            self.db.query(Inventor).filter_by(patent_id=patent.id).delete()
        
        # Add new inventors
        for inventor_data in inventors_data:
            inventor = Inventor(
                patent_id=patent.id,
                name=inventor_data.get("name", ""),
                address=inventor_data.get("address", "")
            )
            self.db.add(inventor)
    
    def _process_ipc_classifications(self, patent: Patent, classifications_data: List[Dict[str, Any]]):
        """Process and store IPC classifications"""
        # Remove existing classifications if updating
        if patent.id:
            self.db.query(IPCClassification).filter_by(patent_id=patent.id).delete()
        
        # Add new classifications
        for classification_data in classifications_data:
            classification = IPCClassification(
                patent_id=patent.id,
                code=classification_data.get("code", ""),
                description=classification_data.get("description", "")
            )
            self.db.add(classification)
    
    def _process_claims(self, patent: Patent, claims_data: List[Dict[str, Any]]):
        """Process and store patent claims"""
        # Remove existing claims if updating
        if patent.id:
            self.db.query(Claim).filter_by(patent_id=patent.id).delete()
        
        # Add new claims
        for i, claim_data in enumerate(claims_data, 1):
            # If claim_data is a string, convert to dict with text
            if isinstance(claim_data, str):
                claim_data = {"text": claim_data, "claim_number": i}
            
            claim = Claim(
                patent_id=patent.id,
                claim_number=claim_data.get("claim_number", i),
                text=claim_data.get("text", "")
            )
            self.db.add(claim)
    
    def _process_descriptions(self, patent: Patent, descriptions_data: List[Dict[str, Any]]):
        """Process and store patent descriptions"""
        # Remove existing descriptions if updating
        if patent.id:
            self.db.query(Description).filter_by(patent_id=patent.id).delete()
        
        # Add new descriptions
        for description_data in descriptions_data:
            # If description_data is a string, convert to dict with text
            if isinstance(description_data, str):
                description_data = {"text": description_data, "section_title": ""}
            
            description = Description(
                patent_id=patent.id,
                section_title=description_data.get("section_title", ""),
                text=description_data.get("text", "")
            )
            self.db.add(description)
    
    def store_patents_batch(self, patents_data: List[Dict[str, Any]]) -> int:
        """
        Store multiple patents in a batch operation
        
        Args:
            patents_data: List of patent data dictionaries
            
        Returns:
            int: Number of patents successfully stored
        """
        success_count = 0
        
        for patent_data in patents_data:
            try:
                if self.store_patent(patent_data):
                    success_count += 1
            except Exception as e:
                logger.error(f"Error storing patent in batch: {str(e)}")
                self.db.rollback()
        
        return success_count
    
    def store_embedding(self, text: str, embedding: List[float], model_id: str) -> Optional[EmbeddingCache]:
        """
        Store text embedding in cache
        
        Args:
            text: Original text
            embedding: Vector embedding
            model_id: Embedding model identifier
            
        Returns:
            EmbeddingCache object if successful, None otherwise
        """
        try:
            # Create hash for the text
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            
            # Check if embedding exists
            existing_embedding = self.db.query(EmbeddingCache).filter_by(
                text_hash=text_hash,
                model_id=model_id
            ).first()
            
            if existing_embedding:
                return existing_embedding
            
            # Store new embedding
            embedding_json = json.dumps(embedding)
            embedding_cache = EmbeddingCache(
                text_hash=text_hash,
                embedding=embedding_json,
                model_id=model_id
            )
            
            self.db.add(embedding_cache)
            self.db.commit()
            self.db.refresh(embedding_cache)
            
            return embedding_cache
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error storing embedding: {str(e)}")
            return None
    
    def get_embedding(self, text: str, model_id: str) -> Optional[List[float]]:
        """
        Get embedding from cache if available
        
        Args:
            text: Text to get embedding for
            model_id: Embedding model identifier
            
        Returns:
            List of floats if found, None otherwise
        """
        # Create hash for the text
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Look up in database
        cached_embedding = self.db.query(EmbeddingCache).filter_by(
            text_hash=text_hash,
            model_id=model_id
        ).first()
        
        if cached_embedding:
            try:
                return json.loads(cached_embedding.embedding)
            except json.JSONDecodeError:
                return None
        
        return None
    
    def search_patents(self, query: Dict[str, Any], limit: int = 20, offset: int = 0) -> List[Patent]:
        """
        Search patents by various criteria
        
        Args:
            query: Dictionary of search parameters
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of patent objects
        """
        q = self.db.query(Patent)
        
        # Apply filters based on query parameters
        if "application_number" in query:
            q = q.filter(Patent.application_number.ilike(f"%{query['application_number']}%"))
        
        if "title" in query:
            q = q.filter(Patent.title.ilike(f"%{query['title']}%"))
        
        if "applicant" in query:
            q = q.join(Patent.applicants).filter(Applicant.name.ilike(f"%{query['applicant']}%"))
        
        if "inventor" in query:
            q = q.join(Patent.inventors).filter(Inventor.name.ilike(f"%{query['inventor']}%"))
        
        if "ipc_code" in query:
            q = q.join(Patent.ipc_classifications).filter(
                IPCClassification.code.ilike(f"%{query['ipc_code']}%")
            )
        
        # Date range filters
        if "application_date_from" in query:
            q = q.filter(Patent.application_date >= query["application_date_from"])
        
        if "application_date_to" in query:
            q = q.filter(Patent.application_date <= query["application_date_to"])
        
        # Sorting
        sort_field = query.get("sort_by", "application_date")
        sort_order = query.get("sort_order", "desc")
        
        if sort_field == "application_date":
            if sort_order.lower() == "asc":
                q = q.order_by(Patent.application_date.asc())
            else:
                q = q.order_by(Patent.application_date.desc())
        elif sort_field == "title":
            if sort_order.lower() == "asc":
                q = q.order_by(Patent.title.asc())
            else:
                q = q.order_by(Patent.title.desc())
        
        # Apply pagination
        q = q.limit(limit).offset(offset)
        
        return q.all()
    
    def get_patent_by_application_number(self, application_number: str) -> Optional[Patent]:
        """Get patent by application number"""
        return self.db.query(Patent).filter_by(application_number=application_number).first()
    
    def get_patents_count(self) -> int:
        """Get total count of patents in database"""
        return self.db.query(Patent).count()
    
    def get_applicants_count(self) -> int:
        """Get total count of unique applicants in database"""
        return self.db.query(sqlalchemy.func.count(sqlalchemy.distinct(Applicant.name))).scalar()
    
    def get_top_applicants(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top applicants by patent count"""
        result = self.db.query(
            Applicant.name,
            sqlalchemy.func.count(Applicant.id).label('patent_count')
        ).group_by(Applicant.name).order_by(text('patent_count DESC')).limit(limit).all()
        
        return [{'name': r[0], 'patent_count': r[1]} for r in result]
    
    def get_patents_by_year(self) -> List[Dict[str, Any]]:
        """Get patent counts by application year"""
        result = self.db.query(
            sqlalchemy.extract('year', Patent.application_date).label('year'),
            sqlalchemy.func.count(Patent.id).label('count')
        ).filter(Patent.application_date.isnot(None)).group_by('year').order_by('year').all()
        
        return [{'year': int(r[0]), 'count': r[1]} for r in result]


def init_db_if_needed():
    """
    Initialize database tables if they don't exist
    """
    from app.patent_system.models import Base, engine
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized.")
