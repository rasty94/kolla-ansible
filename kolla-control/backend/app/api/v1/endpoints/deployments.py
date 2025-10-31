"""
Deployment management endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import Deployment, DeploymentStatus
from app.schemas import (
    DeploymentCreate,
    DeploymentUpdate,
    DeploymentResponse,
    Message,
)

router = APIRouter()


@router.get("/", response_model=List[DeploymentResponse])
async def list_deployments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    List all deployments
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
    """
    result = await db.execute(
        select(Deployment).offset(skip).limit(limit).order_by(Deployment.created_at.desc())
    )
    deployments = result.scalars().all()
    return deployments


@router.post("/", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
async def create_deployment(
    deployment: DeploymentCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new deployment
    
    Args:
        deployment: Deployment configuration
    """
    # Check if deployment with same name exists
    result = await db.execute(
        select(Deployment).where(Deployment.name == deployment.name)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Deployment with name '{deployment.name}' already exists",
        )
    
    # Create new deployment
    db_deployment = Deployment(
        name=deployment.name,
        description=deployment.description,
        globals_config=deployment.globals_config,
        inventory_config=deployment.inventory_config,
        status=DeploymentStatus.PENDING,
    )
    
    db.add(db_deployment)
    await db.commit()
    await db.refresh(db_deployment)
    
    return db_deployment


@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get deployment by ID
    
    Args:
        deployment_id: Deployment ID
    """
    result = await db.execute(
        select(Deployment).where(Deployment.id == deployment_id)
    )
    deployment = result.scalar_one_or_none()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment with ID {deployment_id} not found",
        )
    
    return deployment


@router.put("/{deployment_id}", response_model=DeploymentResponse)
async def update_deployment(
    deployment_id: int,
    deployment_update: DeploymentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update deployment
    
    Args:
        deployment_id: Deployment ID
        deployment_update: Updated deployment data
    """
    result = await db.execute(
        select(Deployment).where(Deployment.id == deployment_id)
    )
    deployment = result.scalar_one_or_none()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment with ID {deployment_id} not found",
        )
    
    # Update fields
    update_data = deployment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deployment, field, value)
    
    await db.commit()
    await db.refresh(deployment)
    
    return deployment


@router.delete("/{deployment_id}", response_model=Message)
async def delete_deployment(
    deployment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete deployment
    
    Args:
        deployment_id: Deployment ID
    """
    result = await db.execute(
        select(Deployment).where(Deployment.id == deployment_id)
    )
    deployment = result.scalar_one_or_none()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment with ID {deployment_id} not found",
        )
    
    await db.delete(deployment)
    await db.commit()
    
    return Message(message=f"Deployment {deployment_id} deleted successfully")
