"""
Socket.IO server configuration
"""
import socketio
from app.core.config import settings

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.BACKEND_CORS_ORIGINS if settings.BACKEND_CORS_ORIGINS else "*",
    logger=True,
    engineio_logger=True
)

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
