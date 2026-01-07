"""
Migration script to add environment_id to existing tables
"""
import asyncio
import logging
from sqlalchemy import text
from app.core.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate():
    async with engine.begin() as conn:
        # Check if environments table exists
        logger.info("Checking schema...")
        
        # Add environment_id to hosts if missing
        try:
            await conn.execute(text("SELECT environment_id FROM hosts LIMIT 1"))
            logger.info("hosts.environment_id already exists")
        except Exception:
            logger.info("Adding environment_id to hosts...")
            await conn.execute(text("ALTER TABLE hosts ADD COLUMN environment_id INTEGER REFERENCES environments(id)"))
            
        # Add environment_id to deployments if missing
        try:
            await conn.execute(text("SELECT environment_id FROM deployments LIMIT 1"))
            logger.info("deployments.environment_id already exists")
        except Exception:
            logger.info("Adding environment_id to deployments...")
            await conn.execute(text("ALTER TABLE deployments ADD COLUMN environment_id INTEGER REFERENCES environments(id)"))
            
    logger.info("Migration completed")

if __name__ == "__main__":
    asyncio.run(migrate())
