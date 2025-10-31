"""
Pydantic schemas for API validation and serialization
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field

from app.models.models import DeploymentStatus, OperationType


# ==================== Deployment Schemas ====================

class DeploymentBase(BaseModel):
    """Base deployment schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    globals_config: Dict[str, Any]
    inventory_config: Dict[str, Any]


class DeploymentCreate(DeploymentBase):
    """Schema for creating a deployment"""
    pass


class DeploymentUpdate(BaseModel):
    """Schema for updating a deployment"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    globals_config: Optional[Dict[str, Any]] = None
    inventory_config: Optional[Dict[str, Any]] = None


class DeploymentInDB(DeploymentBase):
    """Schema for deployment in database"""
    id: int
    status: DeploymentStatus
    current_operation: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


class DeploymentResponse(DeploymentInDB):
    """Schema for deployment API response"""
    pass


# ==================== Host Schemas ====================

class HostBase(BaseModel):
    """Base host schema"""
    hostname: str = Field(..., min_length=1, max_length=255)
    ip_address: str
    ansible_user: str = "root"
    ansible_port: int = 22
    ansible_ssh_private_key_file: Optional[str] = None
    groups: List[str] = Field(default_factory=list)


class HostCreate(HostBase):
    """Schema for creating a host"""
    pass


class HostUpdate(BaseModel):
    """Schema for updating a host"""
    hostname: Optional[str] = Field(None, min_length=1, max_length=255)
    ip_address: Optional[str] = None
    ansible_user: Optional[str] = None
    ansible_port: Optional[int] = None
    ansible_ssh_private_key_file: Optional[str] = None
    groups: Optional[List[str]] = None
    is_active: Optional[bool] = None


class HostInDB(HostBase):
    """Schema for host in database"""
    id: int
    foreman_id: Optional[str]
    foreman_synced_at: Optional[datetime]
    is_active: bool
    last_seen: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HostResponse(HostInDB):
    """Schema for host API response"""
    pass


# ==================== Operation Schemas ====================

class OperationBase(BaseModel):
    """Base operation schema"""
    operation_type: OperationType


class OperationCreate(OperationBase):
    """Schema for creating an operation"""
    deployment_id: int


class OperationInDB(OperationBase):
    """Schema for operation in database"""
    id: int
    deployment_id: int
    celery_task_id: Optional[str]
    status: DeploymentStatus
    progress: int
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    created_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


class OperationResponse(OperationInDB):
    """Schema for operation API response"""
    pass


# ==================== User Schemas ====================

class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """Schema for user in database"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    """Schema for user API response"""
    pass


# ==================== Auth Schemas ====================

class Token(BaseModel):
    """Token schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema"""
    username: str
    password: str


# ==================== Generic Schemas ====================

class Message(BaseModel):
    """Generic message response"""
    message: str


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    version: str
