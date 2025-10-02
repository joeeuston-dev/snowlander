FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libffi-dev \
    libnacl-dev \
    libopus-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/music data/database

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONPATH=/app
ENV MUSIC_DIRECTORY=/app/data/music
ENV DATABASE_PATH=/app/data/database/snowlander.db

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Start the web server in background\n\
python -m uvicorn web.main:app --host 0.0.0.0 --port 8000 &\n\
WEB_PID=$!\n\
\n\
# Start the Discord bot\n\
python -m bot.discord_bot &\n\
BOT_PID=$!\n\
\n\
# Wait for any process to exit\n\
wait -n\n\
\n\
# Exit with status of process that exited first\n\
exit $?\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]
