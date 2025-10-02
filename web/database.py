"""Database initialization and connection management."""

import os
import aiosqlite
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models import Base


class Database:
    """Database connection manager."""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.engine = None
        self.session_maker = None
        
    async def initialize(self):
        """Initialize the database connection and create tables."""
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
        
        # Create async engine
        database_url = f"sqlite+aiosqlite:///{self.database_path}"
        self.engine = create_async_engine(
            database_url,
            echo=False,
            future=True
        )
        
        # Create session maker
        self.session_maker = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def get_session(self):
        """Get a database session."""
        if not self.session_maker:
            await self.initialize()
        return self.session_maker()
    
    async def close(self):
        """Close the database connection."""
        if self.engine:
            await self.engine.dispose()


# Global database instance
db = Database(os.getenv("DATABASE_PATH", "data/database/snowlander.db"))
