"""Main entry point for SNOWLANDER Discord music bot."""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def main():
    """Main function to run both web server and Discord bot."""
    
    # Import after path setup
    from web.main import app
    from bot.discord_bot import run_bot
    import uvicorn
    
    # Start web server in background
    config = uvicorn.Config(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    # Run both server and bot concurrently
    await asyncio.gather(
        server.serve(),
        run_bot(),
        return_exceptions=True
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
