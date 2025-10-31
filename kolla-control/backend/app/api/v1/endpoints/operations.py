"""
Operations endpoints for executing Kolla-Ansible commands
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import Operation, OperationType, Deployment, DeploymentStatus
from app.schemas import OperationResponse, Message
from app.services.kolla_ansible import kolla_ansible_service

router = APIRouter()


@router.post("/{deployment_id}/deploy", response_model=OperationResponse)
async def deploy_openstack(
    deployment_id: int,
    limit: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Deploy OpenStack
    
    Args:
        deployment_id: Deployment ID to deploy
        limit: Limit execution to specific hosts (optional)
    """
    # Get deployment
    result = await db.execute(
        select(Deployment).where(Deployment.id == deployment_id)
    )
    deployment = result.scalar_one_or_none()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found",
        )
    
    # Create operation record
    operation = Operation(
        deployment_id=deployment_id,
        operation_type=OperationType.DEPLOY,
        status=DeploymentStatus.PENDING,
    )
    
    db.add(operation)
    await db.commit()
    await db.refresh(operation)
    
    # TODO: Execute deployment asynchronously using Celery
    # For now, we'll return the operation
    
    return operation


@router.post("/{deployment_id}/upgrade", response_model=OperationResponse)
async def upgrade_openstack(
    deployment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Upgrade OpenStack
    
    Args:
        deployment_id: Deployment ID to upgrade
    """
    result = await db.execute(
        select(Deployment).where(Deployment.id == deployment_id)
    )
    deployment = result.scalar_one_or_none()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found",
        )
    
    operation = Operation(
        deployment_id=deployment_id,
        operation_type=OperationType.UPGRADE,
        status=DeploymentStatus.PENDING,
    )
    
    db.add(operation)
    await db.commit()
    await db.refresh(operation)
    
    return operation


@router.post("/prechecks", response_model=Message)
async def run_prechecks(
    inventory_path: str,
):
    """
    Run prechecks on inventory
    
    Args:
        inventory_path: Path to inventory file
    """
    try:
        result = await kolla_ansible_service.prechecks(inventory=inventory_path)
        
        if result["success"]:
            return Message(message="Prechecks completed successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Prechecks failed: {result['stderr']}",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running prechecks: {str(e)}",
        )


@router.websocket("/ws/{deployment_id}/deploy")
async def deploy_websocket(
    websocket: WebSocket,
    deployment_id: int,
):
    """
    WebSocket endpoint for streaming deployment logs
    
    Args:
        websocket: WebSocket connection
        deployment_id: Deployment ID to deploy
    """
    await websocket.accept()
    
    try:
        # Stream output from deployment
        async for line in kolla_ansible_service.stream_output(
            operation=OperationType.DEPLOY,
            verbose=2,
        ):
            await websocket.send_text(line)
        
        await websocket.close()
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(f"ERROR: {str(e)}")
        await websocket.close()


@router.get("/{operation_id}", response_model=OperationResponse)
async def get_operation_status(
    operation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get operation status
    
    Args:
        operation_id: Operation ID
    """
    result = await db.execute(
        select(Operation).where(Operation.id == operation_id)
    )
    operation = result.scalar_one_or_none()
    
    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operation {operation_id} not found",
        )
    
    return operation
