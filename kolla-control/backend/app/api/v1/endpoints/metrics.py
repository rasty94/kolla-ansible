"""
Metrics API endpoints
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models import Deployment, Host, DeploymentStatus

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard metrics"""
    
    # Counts
    total_deployments = await db.scalar(select(func.count(Deployment.id)))
    active_deployments = await db.scalar(
        select(func.count(Deployment.id)).where(Deployment.status == DeploymentStatus.RUNNING)
    )
    total_hosts = await db.scalar(select(func.count(Host.id)))
    failed_deployments = await db.scalar(
        select(func.count(Deployment.id)).where(Deployment.status == DeploymentStatus.FAILED)
    )
    
    # Calculate success rate
    completed_deployments = await db.scalar(
        select(func.count(Deployment.id)).where(Deployment.status == DeploymentStatus.COMPLETED)
    )
    success_rate = 0
    if total_deployments > 0:
        success_rate = round((completed_deployments / total_deployments) * 100, 1)
        
    # Mock activity data for now (would normally come from Prometheus or historical logs)
    # Generating last 24h mock data
    recent_activity = []
    now = datetime.utcnow()
    for i in range(24):
        time_point = now - timedelta(hours=23-i)
        recent_activity.append({
            "timestamp": time_point.strftime("%H:00"),
            "cpu": 20 + (i % 5) * 10,  # Mock data
            "memory": 40 + (i % 3) * 15, # Mock data
            "deployments": 1 if i % 6 == 0 else 0
        })
        
    return {
        "total_deployments": total_deployments or 0,
        "active_deployments": active_deployments or 0,
        "total_hosts": total_hosts or 0,
        "failed_deployments": failed_deployments or 0,
        "avg_deployment_time": 15, # Mock average time in minutes
        "success_rate": success_rate,
        "recent_activity": recent_activity
    }
