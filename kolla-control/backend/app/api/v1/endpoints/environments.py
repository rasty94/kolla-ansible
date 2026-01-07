"""
Environment management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.models import Environment
from app.schemas import Message

router = APIRouter()

# Schemas
class EnvironmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    config_path: str
    inventory_path: str

class EnvironmentCreate(EnvironmentBase):
    pass

class EnvironmentUpdate(EnvironmentBase):
    name: Optional[str] = None
    config_path: Optional[str] = None
    inventory_path: Optional[str] = None

class EnvironmentResponse(EnvironmentBase):
    id: int
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[EnvironmentResponse])
async def list_environments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all environments"""
    query = select(Environment).offset(skip).limit(limit).order_by(Environment.name)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=EnvironmentResponse, status_code=status.HTTP_201_CREATED)
async def create_environment(
    env: EnvironmentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new environment"""
    # Check if exists
    result = await db.execute(select(Environment).where(Environment.name == env.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Environment already exists")
    
    db_env = Environment(**env.model_dump())
    db.add(db_env)
    await db.commit()
    await db.refresh(db_env)
    return db_env

@router.get("/{env_id}", response_model=EnvironmentResponse)
async def get_environment(
    env_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get environment by ID"""
    result = await db.execute(select(Environment).where(Environment.id == env_id))
    env = result.scalar_one_or_none()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    return env

@router.put("/{env_id}", response_model=EnvironmentResponse)
async def update_environment(
    env_id: int,
    env_update: EnvironmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update environment"""
    result = await db.execute(select(Environment).where(Environment.id == env_id))
    env = result.scalar_one_or_none()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    update_data = env_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(env, field, value)
        
    await db.commit()
    await db.refresh(env)
    return env

@router.delete("/{env_id}", response_model=Message)
async def delete_environment(
    env_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete environment"""
    result = await db.execute(select(Environment).where(Environment.id == env_id))
    env = result.scalar_one_or_none()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    await db.delete(env)
    await db.commit()
    return Message(message=f"Environment {env.name} deleted")
