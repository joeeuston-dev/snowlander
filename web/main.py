"""FastAPI web server for SNOWLANDER Discord bot."""

import os
from typing import List, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from .database import db
from .models import Track, QueueItem, BotStatus, Playlist, PlaylistItem, TrackResponse, QueueItemResponse, BotStatusResponse, PlaylistResponse
from .websocket_manager import ConnectionManager

# Initialize FastAPI app
app = FastAPI(
    title="SNOWLANDER Music Bot",
    description="Discord music bot with web interface",
    version="1.0.0"
)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Mount static files and templates using absolute paths
static_dir = PROJECT_ROOT / "frontend" / "static"
templates_dir = PROJECT_ROOT / "frontend" / "templates"

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# WebSocket connection manager
manager = ConnectionManager()


# Dependency to get database session
async def get_db_session():
    session = await db.get_session()
    try:
        yield session
    finally:
        await session.close()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await db.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database on shutdown."""
    await db.close()


# Web Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/library", response_class=HTMLResponse)
async def library(request: Request):
    """Music library page."""
    return templates.TemplateResponse("library.html", {"request": request})


@app.get("/queue", response_class=HTMLResponse)
async def queue_page(request: Request):
    """Queue management page."""
    return templates.TemplateResponse("queue.html", {"request": request})


@app.get("/playlists", response_class=HTMLResponse)
async def playlists_page(request: Request):
    """Playlists page."""
    return templates.TemplateResponse("playlists.html", {"request": request})


# API Routes
@app.get("/api/status", response_model=BotStatusResponse)
async def get_bot_status(db_session: AsyncSession = Depends(get_db_session)):
    """Get current bot status."""
    result = await db_session.execute(
        select(BotStatus)
        .options(selectinload(BotStatus.current_track))
        .order_by(BotStatus.last_updated.desc())
        .limit(1)
    )
    status = result.scalar_one_or_none()
    
    if not status:
        return BotStatusResponse()
    
    # Get queue length
    queue_result = await db_session.execute(
        select(func.count(QueueItem.id)).where(QueueItem.played == False)
    )
    queue_length = queue_result.scalar() or 0
    
    return BotStatusResponse(
        guild_id=status.guild_id,
        channel_id=status.channel_id,
        is_connected=status.is_connected,
        is_playing=status.is_playing,
        current_track=TrackResponse.model_validate(status.current_track) if status.current_track else None,
        volume=status.volume,
        position=status.position,
        queue_length=queue_length
    )


@app.get("/api/tracks", response_model=List[TrackResponse])
async def get_tracks(
    search: Optional[str] = Query(None, description="Search query"),
    artist: Optional[str] = Query(None, description="Filter by artist"),
    album: Optional[str] = Query(None, description="Filter by album"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    limit: int = Query(50, le=200, description="Number of tracks to return"),
    offset: int = Query(0, ge=0, description="Number of tracks to skip"),
    db_session: AsyncSession = Depends(get_db_session)
):
    """Get tracks with optional filtering."""
    query = select(Track)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (Track.title.ilike(search_filter)) |
            (Track.artist.ilike(search_filter)) |
            (Track.album.ilike(search_filter)) |
            (Track.filename.ilike(search_filter))
        )
    
    if artist:
        query = query.where(Track.artist.ilike(f"%{artist}%"))
    
    if album:
        query = query.where(Track.album.ilike(f"%{album}%"))
    
    if genre:
        query = query.where(Track.genre.ilike(f"%{genre}%"))
    
    # Apply pagination
    query = query.offset(offset).limit(limit).order_by(Track.artist, Track.album, Track.title)
    
    result = await db_session.execute(query)
    tracks = result.scalars().all()
    
    return [TrackResponse.model_validate(track) for track in tracks]


@app.get("/api/queue", response_model=List[QueueItemResponse])
async def get_queue(db_session: AsyncSession = Depends(get_db_session)):
    """Get current queue."""
    result = await db_session.execute(
        select(QueueItem)
        .options(selectinload(QueueItem.track))
        .where(QueueItem.played == False)
        .order_by(QueueItem.position)
    )
    queue_items = result.scalars().all()
    
    return [QueueItemResponse.model_validate(item) for item in queue_items]


@app.post("/api/queue/add/{track_id}")
async def add_to_queue(
    track_id: int,
    requested_by: Optional[str] = None,
    db_session: AsyncSession = Depends(get_db_session)
):
    """Add a track to the queue."""
    # Check if track exists
    track_result = await db_session.execute(select(Track).where(Track.id == track_id))
    track = track_result.scalar_one_or_none()
    
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    # Get next position in queue
    position_result = await db_session.execute(
        select(func.coalesce(func.max(QueueItem.position), 0) + 1)
        .where(QueueItem.played == False)
    )
    next_position = position_result.scalar()
    
    # Create queue item
    queue_item = QueueItem(
        track_id=track_id,
        position=next_position,
        requested_by=requested_by
    )
    
    db_session.add(queue_item)
    await db_session.commit()
    
    # Notify WebSocket clients
    await manager.broadcast({
        "type": "queue_updated",
        "action": "added",
        "track": TrackResponse.model_validate(track).model_dump()
    })
    
    return {"message": "Track added to queue", "position": next_position}


@app.delete("/api/queue/{queue_item_id}")
async def remove_from_queue(
    queue_item_id: int,
    db_session: AsyncSession = Depends(get_db_session)
):
    """Remove a track from the queue."""
    result = await db_session.execute(select(QueueItem).where(QueueItem.id == queue_item_id))
    queue_item = result.scalar_one_or_none()
    
    if not queue_item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    
    await db_session.delete(queue_item)
    await db_session.commit()
    
    # Notify WebSocket clients
    await manager.broadcast({
        "type": "queue_updated",
        "action": "removed",
        "queue_item_id": queue_item_id
    })
    
    return {"message": "Track removed from queue"}


@app.get("/api/playlists", response_model=List[PlaylistResponse])
async def get_playlists(db_session: AsyncSession = Depends(get_db_session)):
    """Get all playlists."""
    result = await db_session.execute(
        select(Playlist, func.count(PlaylistItem.id).label("track_count"))
        .outerjoin(PlaylistItem)
        .group_by(Playlist.id)
        .order_by(Playlist.created_at.desc())
    )
    
    playlists = []
    for playlist, track_count in result:
        playlist_response = PlaylistResponse.model_validate(playlist)
        playlist_response.track_count = track_count or 0
        playlists.append(playlist_response)
    
    return playlists


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()
            # Echo back for now (can add message handling later)
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "web.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
