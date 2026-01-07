"""
Database models
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class DeploymentStatus(str, enum.Enum):
    """Deployment status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OperationType(str, enum.Enum):
    """Operation type enum"""
    DEPLOY = "deploy"
    RECONFIGURE = "reconfigure"
    UPGRADE = "upgrade"
    PULL = "pull"
    DESTROY = "destroy"
    BACKUP = "backup"
    PRECHECKS = "prechecks"
    BOOTSTRAP = "bootstrap"


class Deployment(Base):
    """Deployment model"""
    __tablename__ = "deployments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Configuration
    globals_config = Column(JSON, nullable=False)  # globals.yml content
    inventory_config = Column(JSON, nullable=False)  # inventory structure
    
    # Status
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.PENDING)
    current_operation = Column(String(50), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255), nullable=True)
    
    # Relationships
    operations = relationship("Operation", back_populates="deployment", cascade="all, delete-orphan")


class Host(Base):
    """Host model"""
    __tablename__ = "hosts"
    
    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)  # IPv4 or IPv6
    
    # Host details
    ansible_user = Column(String(255), default="root")
    ansible_port = Column(Integer, default=22)
    ansible_ssh_private_key_file = Column(String(512), nullable=True)
    
    # Groups
    groups = Column(JSON, default=list)  # List of groups this host belongs to
    
    # Foreman integration
    foreman_id = Column(String(255), nullable=True, unique=True)
    foreman_synced_at = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Operation(Base):
    """Operation model - tracks deployment operations"""
    __tablename__ = "operations"
    
    id = Column(Integer, primary_key=True, index=True)
    deployment_id = Column(Integer, ForeignKey("deployments.id"), nullable=False)
    
    # Operation details
    operation_type = Column(Enum(OperationType), nullable=False)
    celery_task_id = Column(String(255), nullable=True, unique=True)
    
    # Status
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.PENDING)
    progress = Column(Integer, default=0)  # 0-100
    
    # Results
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    logs = Column(Text, nullable=True)  # Can store log path or small logs
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(255), nullable=True)
    
    # Relationships
    deployment = relationship("Deployment", back_populates="operations")


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


class AuditLog(Base):
    """Audit log model"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Action details
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    
    # Details
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class Environment(Base):
    """Environment model (Multi-tenancy)"""
    __tablename__ = "environments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Paths
    config_path = Column(String(512), nullable=False)  # e.g. /etc/kolla/env_1
    inventory_path = Column(String(512), nullable=False)  # e.g. /etc/kolla/env_1/inventory
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    hosts = relationship("Host", back_populates="environment", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="environment", cascade="all, delete-orphan")


# Update Host model relationships
Host.environment_id = Column(Integer, ForeignKey("environments.id"), nullable=True)
Host.environment = relationship("Environment", back_populates="hosts")

# Update Deployment model relationships
Deployment.environment_id = Column(Integer, ForeignKey("environments.id"), nullable=True)
Deployment.environment = relationship("Environment", back_populates="deployments")

