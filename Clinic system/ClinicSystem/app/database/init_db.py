"""
Database initialization script
"""

from sqlalchemy.orm import Session
import structlog

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.database.models import Base, User, UserRole, UserStatus

logger = structlog.get_logger()


def init_db() -> None:
    """Initialize database with tables and default data"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
        
        # Create default admin user if not exists
        db = SessionLocal()
        try:
            admin_user = db.query(User).filter(User.email == "admin@clinic.com").first()
            if not admin_user:
                admin_user = User(
                    email="admin@clinic.com",
                    password_hash=get_password_hash("admin123"),
                    first_name="System",
                    last_name="Administrator",
                    role=UserRole.ADMIN,
                    status=UserStatus.ACTIVE
                )
                db.add(admin_user)
                db.commit()
                logger.info("Default admin user created", email="admin@clinic.com")
            else:
                logger.info("Admin user already exists")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        raise


if __name__ == "__main__":
    init_db()
