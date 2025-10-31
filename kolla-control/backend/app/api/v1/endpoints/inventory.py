"""
Inventory management endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import Host
from app.schemas import (
    HostCreate,
    HostUpdate,
    HostResponse,
    Message,
)

router = APIRouter()


@router.get("/hosts", response_model=List[HostResponse])
async def list_hosts(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all hosts
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
    """
    query = select(Host).offset(skip).limit(limit).order_by(Host.hostname)
    
    if is_active is not None:
        query = query.where(Host.is_active == is_active)
    
    result = await db.execute(query)
    hosts = result.scalars().all()
    return hosts


@router.post("/hosts", response_model=HostResponse, status_code=status.HTTP_201_CREATED)
async def create_host(
    host: HostCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Add a new host to inventory
    
    Args:
        host: Host configuration
    """
    # Check if host already exists
    result = await db.execute(
        select(Host).where(Host.hostname == host.hostname)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Host '{host.hostname}' already exists",
        )
    
    # Create new host
    db_host = Host(
        hostname=host.hostname,
        ip_address=host.ip_address,
        ansible_user=host.ansible_user,
        ansible_port=host.ansible_port,
        ansible_ssh_private_key_file=host.ansible_ssh_private_key_file,
        groups=host.groups,
        is_active=True,
    )
    
    db.add(db_host)
    await db.commit()
    await db.refresh(db_host)
    
    return db_host


@router.get("/hosts/{host_id}", response_model=HostResponse)
async def get_host(
    host_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get host by ID
    
    Args:
        host_id: Host ID
    """
    result = await db.execute(
        select(Host).where(Host.id == host_id)
    )
    host = result.scalar_one_or_none()
    
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Host with ID {host_id} not found",
        )
    
    return host


@router.put("/hosts/{host_id}", response_model=HostResponse)
async def update_host(
    host_id: int,
    host_update: HostUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update host configuration
    
    Args:
        host_id: Host ID
        host_update: Updated host data
    """
    result = await db.execute(
        select(Host).where(Host.id == host_id)
    )
    host = result.scalar_one_or_none()
    
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Host with ID {host_id} not found",
        )
    
    # Update fields
    update_data = host_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(host, field, value)
    
    await db.commit()
    await db.refresh(host)
    
    return host


@router.delete("/hosts/{host_id}", response_model=Message)
async def delete_host(
    host_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Remove host from inventory
    
    Args:
        host_id: Host ID
    """
    result = await db.execute(
        select(Host).where(Host.id == host_id)
    )
    host = result.scalar_one_or_none()
    
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Host with ID {host_id} not found",
        )
    
    await db.delete(host)
    await db.commit()
    
    return Message(message=f"Host {host.hostname} deleted successfully")


@router.post("/sync-foreman", response_model=Message)
async def sync_from_foreman(
    db: AsyncSession = Depends(get_db),
):
    """
    Synchronize hosts from Foreman
    
    This endpoint will fetch hosts from Foreman and update the inventory.
    """
    # TODO: Implement Foreman synchronization
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Foreman synchronization not yet implemented",
    )
