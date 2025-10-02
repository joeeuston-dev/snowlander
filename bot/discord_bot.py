"""Discord bot implementation for SNOWLANDER."""

import os
import asyncio
import discord
from discord.ext import commands
from typing import Optional
from datetime import datetime

from web.database import db
from web.models import BotStatus


class SnowlanderBot(commands.Bot):
    """Main Discord bot class."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix=os.getenv("BOT_PREFIX", "!"),
            intents=intents,
            description="SNOWLANDER - Local Music Discord Bot"
        )
        
        self.voice_client: Optional[discord.VoiceClient] = None
        self.current_track = None
        self.queue = []
        self.volume = float(os.getenv("DEFAULT_VOLUME", 0.5))
        
    async def on_ready(self):
        """Called when the bot is ready."""
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is in {len(self.guilds)} guilds')
        
        # Update bot status in database
        await self._update_bot_status()
        
        # Load extensions (commands)
        await self.load_extension('bot.commands')
    
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state updates."""
        if member == self.user:
            # Bot's voice state changed
            if after.channel is None:
                # Bot was disconnected from voice
                self.voice_client = None
                await self._update_bot_status(is_connected=False)
            elif before.channel != after.channel:
                # Bot moved to a different voice channel
                await self._update_bot_status(
                    channel_id=str(after.channel.id),
                    is_connected=True
                )
    
    async def join_voice_channel(self, channel: discord.VoiceChannel):
        """Join a voice channel."""
        if self.voice_client:
            if self.voice_client.channel == channel:
                return self.voice_client
            await self.voice_client.move_to(channel)
        else:
            self.voice_client = await channel.connect()
        
        await self._update_bot_status(
            guild_id=str(channel.guild.id),
            channel_id=str(channel.id),
            is_connected=True
        )
        
        return self.voice_client
    
    async def leave_voice_channel(self):
        """Leave the current voice channel."""
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
            
        await self._update_bot_status(
            is_connected=False,
            is_playing=False,
            current_track_id=None
        )
    
    async def play_track(self, track_path: str, track_id: int = None):
        """Play a track from the local filesystem."""
        if not self.voice_client:
            raise ValueError("Not connected to a voice channel")
        
        if self.voice_client.is_playing():
            self.voice_client.stop()
        
        # Create FFmpeg audio source
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': f'-vn -filter:a "volume={self.volume}"'
        }
        
        audio_source = discord.FFmpegPCMAudio(track_path, **ffmpeg_options)
        
        # Play the track
        self.voice_client.play(
            audio_source,
            after=lambda e: asyncio.create_task(self._on_track_finished(e))
        )
        
        self.current_track = {
            'path': track_path,
            'id': track_id
        }
        
        await self._update_bot_status(
            is_playing=True,
            current_track_id=track_id,
            position=0.0
        )
    
    async def pause_playback(self):
        """Pause the current playback."""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
            await self._update_bot_status(is_playing=False)
    
    async def resume_playback(self):
        """Resume the current playback."""
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
            await self._update_bot_status(is_playing=True)
    
    async def stop_playback(self):
        """Stop the current playback."""
        if self.voice_client and (self.voice_client.is_playing() or self.voice_client.is_paused()):
            self.voice_client.stop()
            
        self.current_track = None
        await self._update_bot_status(
            is_playing=False,
            current_track_id=None,
            position=0.0
        )
    
    async def set_volume(self, volume: float):
        """Set the playback volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        await self._update_bot_status(volume=self.volume)
        
        # If currently playing, the volume change will apply to the next track
        # Real-time volume adjustment would require a different audio source implementation
    
    async def _on_track_finished(self, error):
        """Called when a track finishes playing."""
        if error:
            print(f'Player error: {error}')
        
        self.current_track = None
        await self._update_bot_status(
            is_playing=False,
            current_track_id=None,
            position=0.0
        )
        
        # TODO: Auto-play next track in queue
    
    async def _update_bot_status(self, **kwargs):
        """Update bot status in the database."""
        try:
            async with db.get_session() as session:
                # Get or create bot status record
                from sqlalchemy import select
                result = await session.execute(select(BotStatus).limit(1))
                status = result.scalar_one_or_none()
                
                if not status:
                    status = BotStatus()
                    session.add(status)
                
                # Update fields
                for key, value in kwargs.items():
                    if hasattr(status, key):
                        setattr(status, key, value)
                
                status.last_updated = datetime.utcnow()
                await session.commit()
                
        except Exception as e:
            print(f"Error updating bot status: {e}")


async def run_bot():
    """Run the Discord bot."""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable is required")
    
    bot = SnowlanderBot()
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.close()
    except Exception as e:
        print(f"Bot error: {e}")
        await bot.close()


if __name__ == "__main__":
    asyncio.run(run_bot())
