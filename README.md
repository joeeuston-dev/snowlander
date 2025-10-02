# SNOWLANDER Discord Music Bot

A modern Discord music bot that plays music from your local collection with a beautiful web interface.

## Features

- 🎵 Play music from your local audio collection
- 🌐 Modern web interface for library browsing and queue management
- 📱 Responsive design with Tailwind CSS
- 🔄 Real-time updates via WebSockets
- 📊 Bot status monitoring and control
- 🎚️ Queue management and playlist support (coming soon)
- 🐳 Docker containerized for easy deployment

## Architecture

- **Backend**: FastAPI with async support
- **Bot**: discord.py with voice support
- **Database**: SQLite with SQLAlchemy
- **Frontend**: HTML/JS with Alpine.js and Tailwind CSS
- **Real-time**: WebSocket connections for live updates

## Prerequisites

- Python 3.11+
- FFmpeg
- Discord bot token
- Audio files in supported formats (MP3, FLAC, OGG, WAV, etc.)

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/joeeuston-dev/snowlander.git
   cd snowlander
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp config.example config.env
   # Edit config.env with your settings
   ```

5. **Set environment variables**
   ```bash
   export DISCORD_TOKEN="your_bot_token_here"
   export MUSIC_DIRECTORY="/path/to/your/music"
   export DATABASE_PATH="./data/database/snowlander.db"
   ```

6. **Create sample data for testing**
   ```bash
   python3 tools/sample_data.py
   ```

7. **Run the application**
   
   **Web server only:**
   ```bash
   python3 -m uvicorn web.main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   **Discord bot only:**
   ```bash
   python3 -m bot.discord_bot
   ```
   
   **Both (production-like):**
   ```bash
   # In separate terminals
   python3 -m uvicorn web.main:app --host 0.0.0.0 --port 8000
   python3 -m bot.discord_bot
   ```

8. **Access the web interface**
   ```bash
   open http://localhost:8000
   ```

## Docker Deployment

### **Quick Start with GitHub Container Registry**
```bash
# Use pre-built image from GitHub Container Registry
docker run -d \
  --name snowlander-bot \
  -p 8000:8000 \
  -v /path/to/your/music:/app/data/music:ro \
  -v ./data/database:/app/data/database \
  -e DISCORD_TOKEN=your_bot_token_here \
  ghcr.io/joeeuston-dev/snowlander:latest
```

### **Docker Compose (Recommended)**
```bash
# Download the compose file
wget https://raw.githubusercontent.com/joeeuston-dev/snowlander/main/docker-compose.yml

# Edit with your settings
nano docker-compose.yml

# Run
docker-compose up -d
```

### **Unraid Deployment**
For Unraid users, see the detailed [Unraid Deployment Guide](UNRAID_DEPLOYMENT.md) which covers:
- GitHub Container Registry deployment
- Community Applications installation
- Manual Docker template setup
- Troubleshooting and best practices

### **Build from Source**
```bash
# Clone and build locally
git clone https://github.com/joeeuston-dev/snowlander.git
cd snowlander
docker build -t snowlander .
docker-compose up -d
```

## Configuration

Create a `config.env` file (based on `config.example`):

```bash
# Discord Bot Configuration
DISCORD_TOKEN=your_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here

# Audio Configuration
MUSIC_DIRECTORY=/app/data/music
DATABASE_PATH=/app/data/database/snowlander.db

# Web Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Bot Configuration
BOT_PREFIX=!
DEFAULT_VOLUME=0.5
```

## Bot Commands

- `!join` - Join your voice channel
- `!leave` - Leave the voice channel
- `!play <search>` - Play or queue a track
- `!pause` - Pause playback
- `!resume` - Resume playback
- `!stop` - Stop playback
- `!skip` - Skip current track
- `!queue` - Show current queue
- `!nowplaying` / `!np` - Show current track
- `!search <query>` - Search the music library
- `!volume [0-100]` - Set or show volume
- `!status` - Show bot status
- `!scan` - Scan music library (admin only)

## Web Interface

Access the web interface at `http://localhost:8000`

### Pages:
- **Dashboard** - Bot status, current track, and quick queue view
- **Library** - Browse and search your music collection
- **Queue** - Manage the current queue (coming soon)
- **Playlists** - Create and manage playlists (coming soon)

## API Endpoints

- `GET /api/status` - Bot status
- `GET /api/tracks` - Search tracks with filters
- `GET /api/queue` - Current queue
- `POST /api/queue/add/{track_id}` - Add track to queue
- `DELETE /api/queue/{queue_item_id}` - Remove from queue
- `GET /api/playlists` - List playlists
- `WebSocket /ws` - Real-time updates

## Troubleshooting

### Common Issues

1. **Bot can't connect to Discord**
   - Check your bot token
   - Ensure the bot has proper permissions in your server
   - Verify network connectivity (proxy settings for unraid)

2. **No audio playback**
   - Ensure FFmpeg is installed
   - Check file permissions on music directory
   - Verify audio file formats are supported

3. **Web interface not loading**
   - Check if port 8000 is accessible
   - Verify firewall settings
   - Check application logs

4. **Music library is empty**
   - Run the `!scan` command to index your music
   - Check the `MUSIC_DIRECTORY` path
   - Ensure read permissions on music files

### Logs

View application logs:
```bash
# Docker
docker logs snowlander

# Local development
# Check terminal output where you started the applications
```

## Development

### Project Structure
```
SNOWLANDER/
├── bot/                 # Discord bot code
│   ├── discord_bot.py   # Main bot class
│   ├── commands.py      # Bot commands
│   └── audio_manager.py # Audio processing (TODO)
├── web/                 # Web application
│   ├── main.py          # FastAPI app
│   ├── models.py        # Database models
│   ├── database.py      # Database connection
│   └── websocket_manager.py
├── frontend/            # Web interface
│   ├── templates/       # Jinja2 templates
│   └── static/          # CSS, JS, assets
├── data/                # Runtime data
│   ├── music/           # Music files (mounted)
│   └── database/        # SQLite database
└── docker/              # Docker configuration
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. See LICENSE file for details.

## Acknowledgments

- Built with [discord.py](https://discordpy.readthedocs.io/)
- Web interface powered by [FastAPI](https://fastapi.tiangolo.com/)
- UI styled with [Tailwind CSS](https://tailwindcss.com/)
- Interactivity via [Alpine.js](https://alpinejs.dev/)
- Inspired by [DLAP](https://github.com/Alee14/DLAP)

## Support

For issues and questions, please use the GitHub issues page.
