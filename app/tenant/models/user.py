# app/tenant/models/user.py
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import uuid
import bcrypt

class UserRole(enum.Enum):
    TRENOR_ADMIN = "trenor_admin"      # Platform admin (your team)
    CA_FIRM_ADMIN = "ca_firm_admin"    # CA firm owner/partner
    CA_STAFF = "ca_staff"              # CA firm staff
    CA_VIEWER = "ca_viewer"            # Read-only access
    CLIENT_USER = "client_user"        # Client access (future feature)

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    firm_id = Column(String, ForeignKey("ca_firms.firm_id"), nullable=True)  # Allow NULL for Trenor admins
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CA_STAFF)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    firm = relationship("CAFirm", back_populates="users")
    entity_assignments = relationship("UserEntityMap", back_populates="user", cascade="all, delete-orphan")

    # Password methods
    def set_password(self, password: str):
        """Hash and set password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    # Indexes
    __table_args__ = (
        Index('idx_user_firm_role', 'firm_id', 'role'),
        Index('idx_user_email', 'email'),
        Index('idx_user_active', 'is_active'),
    )

class UserEntityMap(Base):
    __tablename__ = "user_entity_map"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    company_id = Column(String, ForeignKey("entities.company_id"), nullable=False)
    permissions = Column(String, default="read,write")  # comma-separated: read,write,admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="entity_assignments")
    entity = relationship("Entity", back_populates="user_assignments")

    # Indexes
    __table_args__ = (
        Index('idx_user_entity_user', 'user_id'),
        Index('idx_user_entity_company', 'company_id'),
    )