"""Database models for SNOWLANDER music bot."""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

Base = declarative_base()


class Track(Base):
    """Music track model."""
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    filepath = Column(String, nullable=False)
    title = Column(String, index=True)
    artist = Column(String, index=True)
    album = Column(String, index=True)
    genre = Column(String, index=True)
    year = Column(Integer)
    duration = Column(Float)  # Duration in seconds
    file_size = Column(Integer)  # File size in bytes
    format = Column(String)  # File format (mp3, flac, etc.)
    bitrate = Column(Integer)
    sample_rate = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_played = Column(DateTime)
    play_count = Column(Integer, default=0)
    
    # Relationships
    queue_items = relationship("QueueItem", back_populates="track")


class QueueItem(Base):
    """Queue item model."""
    __tablename__ = "queue_items"
    
    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    position = Column(Integer, nullable=False)
    requested_by = Column(String)  # Discord user ID
    requested_at = Column(DateTime, default=datetime.utcnow)
    played = Column(Boolean, default=False)
    
    # Relationships
    track = relationship("Track", back_populates="queue_items")


class Playlist(Base):
    """Playlist model."""
    __tablename__ = "playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    created_by = Column(String)  # Discord user ID
    created_at = Column(DateTime, default=datetime.utcnow)
    is_public = Column(Boolean, default=True)
    
    # Relationships
    items = relationship("PlaylistItem", back_populates="playlist")


class PlaylistItem(Base):
    """Playlist item model."""
    __tablename__ = "playlist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    position = Column(Integer, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    playlist = relationship("Playlist", back_populates="items")
    track = relationship("Track")


class BotStatus(Base):
    """Bot status model."""
    __tablename__ = "bot_status"
    
    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(String)
    channel_id = Column(String)
    is_connected = Column(Boolean, default=False)
    is_playing = Column(Boolean, default=False)
    current_track_id = Column(Integer, ForeignKey("tracks.id"))
    volume = Column(Float, default=0.5)
    position = Column(Float, default=0.0)  # Current playback position in seconds
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    current_track = relationship("Track")


# Pydantic models for API
class TrackResponse(BaseModel):
    id: int
    filename: str
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    duration: Optional[float] = None
    format: Optional[str] = None
    play_count: int = 0
    
    model_config = {"from_attributes": True}


class QueueItemResponse(BaseModel):
    id: int
    track: TrackResponse
    position: int
    requested_by: Optional[str] = None
    requested_at: datetime
    played: bool = False
    
    model_config = {"from_attributes": True}


class BotStatusResponse(BaseModel):
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    is_connected: bool = False
    is_playing: bool = False
    current_track: Optional[TrackResponse] = None
    volume: float = 0.5
    position: float = 0.0
    queue_length: int = 0
    
    model_config = {"from_attributes": True}


class PlaylistResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    is_public: bool = True
    track_count: int = 0
    
    model_config = {"from_attributes": True}
