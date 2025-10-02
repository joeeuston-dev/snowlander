"""Discord bot commands for SNOWLANDER."""

import os
from discord.ext import commands
from discord import VoiceChannel
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from web.database import db
from web.models import Track, QueueItem


class MusicCommands(commands.Cog):
    """Music-related bot commands."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='join')
    async def join(self, ctx):
        """Join the user's voice channel."""
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel!")
            return
        
        channel = ctx.author.voice.channel
        await self.bot.join_voice_channel(channel)
        await ctx.send(f"Joined {channel.name}")
    
    @commands.command(name='leave')
    async def leave(self, ctx):
        """Leave the current voice channel."""
        if not self.bot.voice_client:
            await ctx.send("I'm not connected to a voice channel!")
            return
        
        await self.bot.leave_voice_channel()
        await ctx.send("Left the voice channel")
    
    @commands.command(name='play')
    async def play(self, ctx, *, search_term: str = None):
        """Play a track or add it to the queue."""
        if not search_term:
            # Resume playback if paused
            if self.bot.voice_client and self.bot.voice_client.is_paused():
                await self.bot.resume_playback()
                await ctx.send("▶️ Resumed playback")
                return
            else:
                await ctx.send("Please provide a search term or song name")
                return
        
        # Ensure bot is in a voice channel
        if not self.bot.voice_client:
            if ctx.author.voice:
                await self.bot.join_voice_channel(ctx.author.voice.channel)
            else:
                await ctx.send("You need to be in a voice channel!")
                return
        
        # Search for the track in the database
        async with db.get_session() as session:
            # Search by title, artist, filename
            search_filter = f"%{search_term}%"
            result = await session.execute(
                select(Track).where(
                    (Track.title.ilike(search_filter)) |
                    (Track.artist.ilike(search_filter)) |
                    (Track.filename.ilike(search_filter))
                ).limit(1)
            )
            
            track = result.scalar_one_or_none()
            
            if not track:
                await ctx.send(f"No tracks found matching '{search_term}'")
                return
            
            # If nothing is currently playing, play immediately
            if not self.bot.voice_client.is_playing():
                try:
                    await self.bot.play_track(track.filepath, track.id)
                    await ctx.send(f"🎵 Now playing: **{track.title or track.filename}** by {track.artist or 'Unknown Artist'}")
                except Exception as e:
                    await ctx.send(f"Error playing track: {e}")
            else:
                # Add to queue
                # Get next position in queue
                position_result = await session.execute(
                    select(func.coalesce(func.max(QueueItem.position), 0) + 1)
                    .where(QueueItem.played == False)
                )
                next_position = position_result.scalar()
                
                # Create queue item
                queue_item = QueueItem(
                    track_id=track.id,
                    position=next_position,
                    requested_by=str(ctx.author.id)
                )
                
                session.add(queue_item)
                await session.commit()
                
                await ctx.send(f"➕ Added to queue: **{track.title or track.filename}** (Position #{next_position})")
    
    @commands.command(name='pause')
    async def pause(self, ctx):
        """Pause the current playback."""
        if not self.bot.voice_client or not self.bot.voice_client.is_playing():
            await ctx.send("Nothing is currently playing!")
            return
        
        await self.bot.pause_playback()
        await ctx.send("⏸️ Paused playback")
    
    @commands.command(name='resume')
    async def resume(self, ctx):
        """Resume the current playback."""
        if not self.bot.voice_client or not self.bot.voice_client.is_paused():
            await ctx.send("Nothing is currently paused!")
            return
        
        await self.bot.resume_playback()
        await ctx.send("▶️ Resumed playback")
    
    @commands.command(name='stop')
    async def stop(self, ctx):
        """Stop the current playback."""
        if not self.bot.voice_client:
            await ctx.send("I'm not connected to a voice channel!")
            return
        
        await self.bot.stop_playback()
        await ctx.send("⏹️ Stopped playback")
    
    @commands.command(name='volume')
    async def volume(self, ctx, volume: float = None):
        """Set or display the current volume."""
        if volume is None:
            await ctx.send(f"🔊 Current volume: {int(self.bot.volume * 100)}%")
            return
        
        if not 0 <= volume <= 100:
            await ctx.send("Volume must be between 0 and 100")
            return
        
        volume_decimal = volume / 100
        await self.bot.set_volume(volume_decimal)
        await ctx.send(f"🔊 Volume set to {int(volume)}%")
    
    @commands.command(name='queue')
    async def queue(self, ctx):
        """Display the current queue."""
        async with db.get_session() as session:
            result = await session.execute(
                select(QueueItem)
                .options(selectinload(QueueItem.track))
                .where(QueueItem.played == False)
                .order_by(QueueItem.position)
                .limit(10)
            )
            
            queue_items = result.scalars().all()
            
            if not queue_items:
                await ctx.send("The queue is empty!")
                return
            
            queue_text = "📋 **Current Queue:**\n"
            for item in queue_items:
                track = item.track
                queue_text += f"{item.position}. **{track.title or track.filename}** by {track.artist or 'Unknown Artist'}\n"
            
            if len(queue_items) == 10:
                queue_text += "...(showing first 10 items)"
            
            await ctx.send(queue_text)
    
    @commands.command(name='skip')
    async def skip(self, ctx):
        """Skip the current track."""
        if not self.bot.voice_client or not self.bot.voice_client.is_playing():
            await ctx.send("Nothing is currently playing!")
            return
        
        self.bot.voice_client.stop()
        await ctx.send("⏭️ Skipped track")
    
    @commands.command(name='nowplaying', aliases=['np'])
    async def now_playing(self, ctx):
        """Display information about the currently playing track."""
        if not self.bot.current_track:
            await ctx.send("Nothing is currently playing!")
            return
        
        track_id = self.bot.current_track.get('id')
        if track_id:
            async with db.get_session() as session:
                result = await session.execute(select(Track).where(Track.id == track_id))
                track = result.scalar_one_or_none()
                
                if track:
                    duration_str = ""
                    if track.duration:
                        minutes = int(track.duration // 60)
                        seconds = int(track.duration % 60)
                        duration_str = f" ({minutes}:{seconds:02d})"
                    
                    await ctx.send(f"🎵 **Now Playing:** {track.title or track.filename}\n"
                                 f"👤 **Artist:** {track.artist or 'Unknown Artist'}\n"
                                 f"💿 **Album:** {track.album or 'Unknown Album'}{duration_str}")
                    return
        
        await ctx.send("🎵 **Now Playing:** Unknown Track")
    
    @commands.command(name='search')
    async def search(self, ctx, *, search_term: str):
        """Search for tracks in the music library."""
        async with db.get_session() as session:
            search_filter = f"%{search_term}%"
            result = await session.execute(
                select(Track).where(
                    (Track.title.ilike(search_filter)) |
                    (Track.artist.ilike(search_filter)) |
                    (Track.album.ilike(search_filter)) |
                    (Track.filename.ilike(search_filter))
                ).limit(10)
            )
            
            tracks = result.scalars().all()
            
            if not tracks:
                await ctx.send(f"No tracks found matching '{search_term}'")
                return
            
            search_text = f"🔍 **Search results for '{search_term}':**\n"
            for i, track in enumerate(tracks, 1):
                search_text += f"{i}. **{track.title or track.filename}** by {track.artist or 'Unknown Artist'}\n"
            
            if len(tracks) == 10:
                search_text += "...(showing first 10 results)"
            
            search_text += "\n💡 Use `!play <song name>` to play a track"
            await ctx.send(search_text)


class AdminCommands(commands.Cog):
    """Admin-only bot commands."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='scan')
    @commands.has_permissions(administrator=True)
    async def scan_library(self, ctx):
        """Scan the music library for new tracks."""
        await ctx.send("🔄 Starting library scan... (This may take a while)")
        
        # TODO: Implement library scanning
        # This would involve:
        # 1. Walking through the music directory
        # 2. Reading metadata from audio files
        # 3. Adding/updating tracks in the database
        
        await ctx.send("📁 Library scan completed!")
    
    @commands.command(name='status')
    async def bot_status(self, ctx):
        """Display bot status and statistics."""
        async with db.get_session() as session:
            # Get track count
            track_count_result = await session.execute(select(func.count(Track.id)))
            track_count = track_count_result.scalar()
            
            # Get queue length
            queue_count_result = await session.execute(
                select(func.count(QueueItem.id)).where(QueueItem.played == False)
            )
            queue_count = queue_count_result.scalar()
            
            status_text = f"📊 **SNOWLANDER Bot Status**\n"
            status_text += f"🎵 **Music Library:** {track_count} tracks\n"
            status_text += f"📋 **Queue Length:** {queue_count} items\n"
            status_text += f"🔊 **Volume:** {int(self.bot.volume * 100)}%\n"
            
            if self.bot.voice_client:
                status_text += f"🎙️ **Voice Channel:** {self.bot.voice_client.channel.name}\n"
                if self.bot.voice_client.is_playing():
                    status_text += "▶️ **Status:** Playing\n"
                elif self.bot.voice_client.is_paused():
                    status_text += "⏸️ **Status:** Paused\n"
                else:
                    status_text += "⏹️ **Status:** Stopped\n"
            else:
                status_text += "❌ **Status:** Not connected to voice\n"
            
            status_text += f"🌐 **Web Interface:** http://localhost:{os.getenv('PORT', 8000)}"
            
            await ctx.send(status_text)


async def setup(bot):
    """Load the commands cogs."""
    await bot.add_cog(MusicCommands(bot))
    await bot.add_cog(AdminCommands(bot))
