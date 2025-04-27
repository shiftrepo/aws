import os
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
import sqlalchemy.exc

from app.patent_system.jplatpat.models import (
    Base, engine, SessionLocal, Patent, Applicant, Inventor, 
    IPCClassification, Claim, Description, ensure_db_exists
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DBManager:
    """Manager for SQLite database operations"""
    
    def __init__(self):
        """Initialize the database manager"""
        self.db_path = ensure_db_exists()
        self.db = None
    
    def __enter__(self):
        """Context manager entry"""
        self.db = SessionLocal()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.db:
            self.db.close()
    
    def store_patent(self, patent_data: Dict[str, Any]) -> Optional[Patent]:
        """
        Store a single patent in the database
        
        Args:
            patent_data: Dictionary with patent data
            
        Returns:
            Patent object if successful, None if failed
        """
        try:
            # Check if patent already exists (by application number)
            application_number = patent_data.get("application_number")
            if not application_number:
                logger.error("Cannot store patent: No application number provided")
                return None
                
            existing = self.db.query(Patent).filter(
                Patent.application_number == application_number
            ).first()
            
            if existing:
                logger.info(f"Patent {application_number} already exists, updating...")
                patent = existing
            else:
                logger.info(f"Creating new patent record for {application_number}")
                patent = Patent(
                    application_number=application_number
                )
            
            # Update fields
            patent.title = patent_data.get("title")
            patent.abstract = patent_data.get("abstract")
            
            # Parse dates if provided as strings
            app_date = patent_data.get("application_date")
            if app_date and isinstance(app_date, str):
                try:
                    patent.application_date = datetime.fromisoformat(app_date)
                except (ValueError, TypeError):
                    try:
                        # Try different format
                        patent.application_date = datetime.strptime(app_date, "%Y-%m-%d")
                    except (ValueError, TypeError):
                        patent.application_date = None
            
            pub_date = patent_data.get("publication_date")
            if pub_date and isinstance(pub_date, str):
                try:
                    patent.publication_date = datetime.fromisoformat(pub_date)
                except (ValueError, TypeError):
                    try:
                        # Try different format
                        patent.publication_date = datetime.strptime(pub_date, "%Y-%m-%d")
                    except (ValueError, TypeError):
                        patent.publication_date = None
            
            patent.publication_number = patent_data.get("publication_number")
            patent.registration_number = patent_data.get("registration_number")
            
            reg_date = patent_data.get("registration_date")
            if reg_date and isinstance(reg_date, str):
                try:
                    patent.registration_date = datetime.fromisoformat(reg_date)
                except (ValueError, TypeError):
                    try:
                        # Try different format
                        patent.registration_date = datetime.strptime(reg_date, "%Y-%m-%d")
                    except (ValueError, TypeError):
                        patent.registration_date = None
            
            # Update timestamp
            patent.updated_at = datetime.utcnow()
            
            # If new patent, add to session
            if not existing:
                self.db.add(patent)
                self.db.flush()  # Get ID without committing
            
            # Handle related entities - first remove existing ones if updating
            if existing:
                # Delete existing applicants, inventors, etc.
                self.db.query(Applicant).filter(Applicant.patent_id == patent.id).delete()
                self.db.query(Inventor).filter(Inventor.patent_id == patent.id).delete()
                self.db.query(IPCClassification).filter(IPCClassification.patent_id == patent.id).delete()
                self.db.query(Claim).filter(Claim.patent_id == patent.id).delete()
                self.db.query(Description).filter(Description.patent_id == patent.id).delete()
            
            # Add applicants
            applicants_data = patent_data.get("applicants", [])
            if not applicants_data and "applicant_name" in patent_data:
                # Support for simpler format with single applicant
                applicants_data = [{"name": patent_data["applicant_name"]}]
                
            for app_data in applicants_data:
                applicant = Applicant(
                    patent_id=patent.id,
                    name=app_data.get("name", ""),
                    address=app_data.get("address", "")
                )
                self.db.add(applicant)
            
            # Add inventors
            inventors_data = patent_data.get("inventors", [])
            if not inventors_data and "inventor_name" in patent_data:
                # Support for simpler format with single inventor
                inventors_data = [{"name": patent_data["inventor_name"]}]
                
            for inv_data in inventors_data:
                inventor = Inventor(
                    patent_id=patent.id,
                    name=inv_data.get("name", ""),
                    address=inv_data.get("address", "")
                )
                self.db.add(inventor)
            
            # Add IPC classifications
            ipc_data = patent_data.get("ipc_classifications", [])
            if not ipc_data and "ipc" in patent_data:
                # Support for simpler format with single IPC code
                ipc_data = [{"code": patent_data["ipc"]}]
                
            for ipc in ipc_data:
                classification = IPCClassification(
                    patent_id=patent.id,
                    code=ipc.get("code", ""),
                    description=ipc.get("description", "")
                )
                self.db.add(classification)
            
            # Add claims
            claims_data = patent_data.get("claims", [])
            for idx, claim_data in enumerate(claims_data):
                claim_number = claim_data.get("claim_number", idx+1) if isinstance(claim_data, dict) else idx+1
                text = claim_data.get("text") if isinstance(claim_data, dict) else claim_data
                
                claim = Claim(
                    patent_id=patent.id,
                    claim_number=claim_number,
                    text=text
                )
                self.db.add(claim)
            
            # Add descriptions
            desc_data = patent_data.get("descriptions", [])
            for idx, desc_data_item in enumerate(desc_data):
                section_title = None
                text = None
                
                if isinstance(desc_data_item, dict):
                    section_title = desc_data_item.get("section_title", f"Section {idx+1}")
                    text = desc_data_item.get("text", "")
                else:
                    section_title = f"Section {idx+1}"
                    text = desc_data_item
                
                description = Description(
                    patent_id=patent.id,
                    section_title=section_title,
                    text=text
                )
                self.db.add(description)
            
            # Commit changes
            self.db.commit()
            logger.info(f"Successfully stored patent {application_number}")
            
            return patent
            
        except sqlalchemy.exc.SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error storing patent: {str(e)}")
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error storing patent: {str(e)}")
            return None
    
    def store_patents_batch(self, patents_data: List[Dict[str, Any]]) -> int:
        """
        Store multiple patents in the database
        
        Args:
            patents_data: List of dictionaries with patent data
            
        Returns:
            int: Number of patents successfully stored
        """
        success_count = 0
        
        for patent_data in patents_data:
            try:
                patent = self.store_patent(patent_data)
                if patent:
                    success_count += 1
            except Exception as e:
                logger.error(f"Error storing patent: {str(e)}")
        
        logger.info(f"Successfully stored {success_count}/{len(patents_data)} patents")
        return success_count
    
    def get_patent_by_application_number(self, application_number: str) -> Optional[Patent]:
        """
        Get a patent by application number
        
        Args:
            application_number: Patent application number
            
        Returns:
            Patent object if found, None otherwise
        """
        try:
            return self.db.query(Patent).filter(
                Patent.application_number == application_number
            ).first()
        except Exception as e:
            logger.error(f"Error getting patent by application number: {str(e)}")
            return None
    
    def get_patents_by_applicant(self, applicant_name: str, limit: int = 100) -> List[Patent]:
        """
        Get patents by applicant name
        
        Args:
            applicant_name: Name of the applicant
            limit: Maximum number of patents to retrieve
            
        Returns:
            List of Patent objects
        """
        try:
            return self.db.query(Patent).join(
                Applicant
            ).filter(
                Applicant.name.like(f"%{applicant_name}%")
            ).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting patents by applicant: {str(e)}")
            return []
    
    def search_patents(self, query: str, limit: int = 100) -> List[Patent]:
        """
        Search patents by title, abstract, or applicant name
        
        Args:
            query: Search query string
            limit: Maximum number of patents to retrieve
            
        Returns:
            List of Patent objects
        """
        try:
            # Search in title, abstract, applicant name
            results = self.db.query(Patent).filter(
                Patent.title.like(f"%{query}%") | 
                Patent.abstract.like(f"%{query}%")
            ).limit(limit).all()
            
            # Also search in applicant names
            applicant_results = self.db.query(Patent).join(
                Applicant
            ).filter(
                Applicant.name.like(f"%{query}%")
            ).limit(limit).all()
            
            # Combine results, removing duplicates
            all_patents = {}
            for patent in results + applicant_results:
                all_patents[patent.id] = patent
                
            return list(all_patents.values())[:limit]
        except Exception as e:
            logger.error(f"Error searching patents: {str(e)}")
            return []
    
    def get_all_patents(self, limit: int = 1000) -> List[Patent]:
        """
        Get all patents in the database
        
        Args:
            limit: Maximum number of patents to retrieve
            
        Returns:
            List of Patent objects
        """
        try:
            return self.db.query(Patent).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting all patents: {str(e)}")
            return []
    
    def count_patents(self) -> int:
        """
        Count the number of patents in the database
        
        Returns:
            Number of patents
        """
        try:
            return self.db.query(Patent).count()
        except Exception as e:
            logger.error(f"Error counting patents: {str(e)}")
            return 0


def reset_db():
    """
    Reset the database by dropping all tables and recreating them.
    This will delete all data in the database.
    """
    try:
        logger.warning("Dropping all tables in the database...")
        Base.metadata.drop_all(bind=engine)
        logger.info("All tables dropped successfully")
        
        logger.info("Recreating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database reset completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        return False


def init_db():
    """Initialize SQLite database if not exists"""
    ensure_db_exists()
    logger.info("SQLite database initialized")


if __name__ == "__main__":
    # Test database operations
    init_db()
    
    with DBManager() as db:
        # Check if database is empty
        count = db.count_patents()
        print(f"Current patent count: {count}")
        
        if count == 0:
            # Add a test patent
            test_patent = {
                "application_number": "2020-123456",
                "application_date": "2020-06-01",
                "publication_number": "JP2022-123456A",
                "publication_date": "2022-01-15",
                "title": "テスト特許",
                "abstract": "これはテスト用の特許データです。",
                "applicants": [
                    {"name": "テスト株式会社", "address": "東京都千代田区"}
                ],
                "inventors": [
                    {"name": "発明 太郎", "address": "東京都千代田区"}
                ],
                "ipc_classifications": [
                    {"code": "G06F 16/00", "description": "情報検索"}
                ],
                "claims": [
                    {"claim_number": 1, "text": "これはテスト請求項です。"}
                ],
                "descriptions": [
                    {"section_title": "技術分野", "text": "これはテスト技術分野の説明です。"}
                ]
            }
            
            patent = db.store_patent(test_patent)
            if patent:
                print(f"Added test patent: {patent.title}")
            
            count = db.count_patents()
            print(f"Updated patent count: {count}")
