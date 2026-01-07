"""
API v1 router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import deployments, operations, inventory, health, config, auth, environments, metrics

api_router = APIRouter()

# Include routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"],
)

api_router.include_router(
    health.router,
    tags=["health"],
)

api_router.include_router(
    deployments.router,
    prefix="/deployments",
    tags=["deployments"],
)

api_router.include_router(
    operations.router,
    prefix="/operations",
    tags=["operations"],
)

api_router.include_router(
    inventory.router,
    prefix="/inventory",
    tags=["inventory"],
)

api_router.include_router(
    config.router,
    prefix="/config",
    tags=["config"],
)

api_router.include_router(
    environments.router,
    prefix="/environments",
    tags=["environments"],
)

api_router.include_router(
    metrics.router,
    prefix="/metrics",
    tags=["metrics"],
)
