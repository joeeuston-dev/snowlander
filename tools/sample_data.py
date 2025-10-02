"""Sample data generator for testing SNOWLANDER."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from web.database import db
from web.models import Track, BotStatus


async def create_sample_data():
    """Create sample tracks in the database for testing."""
    
    # Initialize database
    await db.initialize()
    
    sample_tracks = [
        {
            "filename": "sample_track_1.mp3",
            "filepath": "/app/data/music/sample_artist/sample_album/sample_track_1.mp3",
            "title": "Epic Journey",
            "artist": "Demo Artist",
            "album": "Sample Album",
            "genre": "Electronic",
            "year": 2023,
            "duration": 240.5,
            "file_size": 3840000,
            "format": "mp3",
            "bitrate": 320,
            "sample_rate": 44100
        },
        {
            "filename": "sample_track_2.mp3",
            "filepath": "/app/data/music/sample_artist/sample_album/sample_track_2.mp3",
            "title": "Digital Dreams",
            "artist": "Demo Artist",
            "album": "Sample Album",
            "genre": "Electronic",
            "year": 2023,
            "duration": 195.8,
            "file_size": 3120000,
            "format": "mp3",
            "bitrate": 320,
            "sample_rate": 44100
        },
        {
            "filename": "another_song.flac",
            "filepath": "/app/data/music/another_artist/another_song.flac",
            "title": "Test Song",
            "artist": "Another Artist",
            "album": "Single",
            "genre": "Rock",
            "year": 2022,
            "duration": 180.2,
            "file_size": 25600000,
            "format": "flac",
            "bitrate": 1411,
            "sample_rate": 44100
        },
        {
            "filename": "instrumental.ogg",
            "filepath": "/app/data/music/instrumental_artist/instrumental.ogg",
            "title": "Peaceful Melody",
            "artist": "Instrumental Artist",
            "album": "Ambient Collection",
            "genre": "Ambient",
            "year": 2024,
            "duration": 320.1,
            "file_size": 4560000,
            "format": "ogg",
            "bitrate": 192,
            "sample_rate": 44100
        },
        {
            "filename": "unknown_track.wav",
            "filepath": "/app/data/music/unknown/unknown_track.wav",
            "title": None,
            "artist": None,
            "album": None,
            "genre": None,
            "year": None,
            "duration": 145.3,
            "file_size": 15400000,
            "format": "wav",
            "bitrate": None,
            "sample_rate": 44100
        }
    ]
    
    session = await db.get_session()
    try:
        # Clear existing tracks
        from sqlalchemy import text
        await session.execute(text("DELETE FROM tracks"))
        
        # Add sample tracks
        for track_data in sample_tracks:
            track = Track(**track_data)
            session.add(track)
        
        # Create initial bot status
        await session.execute(text("DELETE FROM bot_status"))
        initial_status = BotStatus(
            is_connected=False,
            is_playing=False,
            volume=0.5
        )
        session.add(initial_status)
        
        await session.commit()
        print(f"✅ Created {len(sample_tracks)} sample tracks")
        print("✅ Created initial bot status")
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(create_sample_data())
