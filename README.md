# SNOWLANDER

A Discord music bot with web interface for managing and playing music from your local collection.

## Features

- **Discord Bot**: Play music in voice channels with standard commands
- **Web Interface**: Browse library, manage queue, and control playback
- **Real-time Updates**: WebSocket connections for live status updates
- **Queue Management**: Add, remove, and reorder tracks
- **Search & Filter**: Find music quickly in large collections
- **Playlist Support**: Create and manage custom playlists

## Quick Start

### Prerequisites

- Python 3.9+
- FFmpeg installed and in PATH
- Discord bot token
- Music collection directory

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/joeeuston-dev/snowlander.git
   cd snowlander
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp config.example .env
   # Edit .env with your settings
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

The web interface will be available at `http://localhost:8000`

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Or use pre-built image**
   ```bash
   docker run -d \
     --name snowlander \
     -p 8000:8000 \
     -v /path/to/music:/app/data/music:ro \
     -v ./data:/app/data/database \
     -e DISCORD_TOKEN=your_bot_token \
     ghcr.io/joeeuston-dev/snowlander:latest
   ```

## Configuration

Required environment variables:

- `DISCORD_TOKEN`: Your Discord bot token
- `MUSIC_DIR`: Path to your music collection (default: `/app/data/music`)
- `DATABASE_URL`: SQLite database path (default: `sqlite+aiosqlite:///./data/bot.db`)

Optional:
- `WEB_PORT`: Web interface port (default: `8000`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

## Discord Commands

- `!play <search>` - Play or search for music
- `!pause` / `!resume` - Control playback
- `!skip` - Skip current track
- `!queue` - Show current queue
- `!nowplaying` - Show current track info
- `!join` / `!leave` - Voice channel management
- `!scan` - Rescan music library

## Development

### Local Development

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create sample data**
   ```bash
   python tools/sample_data.py
   ```

### Project Structure

```
snowlander/
├── bot/                 # Discord bot implementation
├── web/                 # FastAPI web application
├── frontend/            # Web interface templates
├── tools/               # Development utilities
├── main.py              # Application entry point
├── docker-compose.yml   # Docker deployment
└── Dockerfile          # Container definition
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please use the GitHub issue tracker.
