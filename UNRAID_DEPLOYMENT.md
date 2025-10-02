# SNOWLANDER Unraid Deployment Guide

This guide covers multiple ways to deploy SNOWLANDER on your Unraid server.

## 🚀 **Option 1: GitHub Container Registry (Recommended)**

### **Automatic Builds**
Every time you push to the main branch, GitHub Actions automatically builds and pushes a Docker image to `ghcr.io/joeeuston-dev/snowlander:latest`.

### **Quick Deployment**

1. **SSH into your Unraid server**
   ```bash
   ssh root@your-unraid-ip
   ```

2. **Create deployment directory**
   ```bash
   mkdir -p /mnt/user/appdata/snowlander
   cd /mnt/user/appdata/snowlander
   ```

3. **Download the Unraid docker-compose file**
   ```bash
   wget https://raw.githubusercontent.com/joeeuston-dev/snowlander/main/docker-compose.unraid.yml
   wget https://raw.githubusercontent.com/joeeuston-dev/snowlander/main/unraid.env.example
   ```

4. **Create your environment file**
   ```bash
   cp unraid.env.example .env
   nano .env  # Edit with your Discord token and settings
   ```

5. **Adjust music share path in docker-compose.unraid.yml**
   ```bash
   nano docker-compose.unraid.yml
   # Change /mnt/user/Music to your actual music share path
   ```

6. **Deploy the container**
   ```bash
   docker-compose -f docker-compose.unraid.yml up -d
   ```

7. **Access the web interface**
   ```
   http://your-unraid-ip:8000
   ```

### **Verify GitHub Container Registry**

You can check available images and versions:
```bash
# List available tags
curl -s "https://ghcr.io/v2/joeeuston-dev/snowlander/tags/list" | jq

# Pull specific versions
docker pull ghcr.io/joeeuston-dev/snowlander:latest    # Default optimized
docker pull ghcr.io/joeeuston-dev/snowlander:alpine    # Lightweight Alpine
```

## 🐳 **Option 2: Unraid Community Applications**

### **Install via CA (Community Applications)**

1. **Search for "SNOWLANDER" in Community Applications**
2. **Click Install**
3. **Configure the template**:
   - **Repository**: `ghcr.io/joeeuston-dev/snowlander:latest`
   - **Discord Token**: Your bot token
   - **Music Path**: Path to your music share (e.g., `/mnt/user/Music/`)
   - **WebUI Port**: `8000`

## 🛠️ **Option 3: Manual Docker Template**

### **Create Custom Docker Template**

1. **Go to Unraid Docker tab**
2. **Click "Add Container"**
3. **Fill in the template**:

```
Name: SNOWLANDER
Repository: ghcr.io/joeeuston-dev/snowlander:latest
Network Type: Bridge
Console Shell Command: Bash

Port Mappings:
- Container Port: 8000, Host Port: 8000, Protocol: TCP

Path Mappings:
- Container Path: /app/data/music, Host Path: /mnt/user/Music, Access Mode: Read Only
- Container Path: /app/data/database, Host Path: /mnt/user/appdata/snowlander, Access Mode: Read/Write

Environment Variables:
- Key: DISCORD_TOKEN, Value: your_bot_token_here
- Key: MUSIC_DIRECTORY, Value: /app/data/music
- Key: DATABASE_PATH, Value: /app/data/database/snowlander.db
- Key: HOST, Value: 0.0.0.0
- Key: PORT, Value: 8000
- Key: BOT_PREFIX, Value: !
- Key: DEFAULT_VOLUME, Value: 0.5
```

## 🔧 **Option 4: Build from Source on Unraid**

### **For Development/Customization**

1. **Install git and docker-compose on Unraid**
   ```bash
   # Install via Nerd Tools plugin or manually
   ```

2. **Clone and build**
   ```bash
   cd /mnt/user/appdata
   git clone https://github.com/joeeuston-dev/snowlander.git
   cd snowlander
   
   # Edit docker-compose.yml with your paths
   nano docker-compose.yml
   
   # Build and run
   docker-compose up -d --build
   ```

## 📋 **Configuration Details**

### **Required Environment Variables**
- `DISCORD_TOKEN`: Your Discord bot token

### **Optional Environment Variables**
- `DISCORD_GUILD_ID`: Your Discord server ID
- `BOT_PREFIX`: Command prefix (default: `!`)
- `DEFAULT_VOLUME`: Initial volume (default: `0.5`)

### **Volume Mappings**
- **Music Library**: `/mnt/user/Music` → `/app/data/music` (read-only)
- **Database**: `/mnt/user/appdata/snowlander` → `/app/data/database` (read-write)
- **Logs** (optional): `/mnt/user/appdata/snowlander/logs` → `/app/logs`

### **Common Music Share Paths**
- `/mnt/user/Music`
- `/mnt/user/media/Music`
- `/mnt/user/shares/Music`
- `/mnt/disk1/Music` (specific disk)

## 🔍 **Troubleshooting**

### **Container Won't Start**
```bash
# Check logs
docker logs snowlander-bot

# Check if port is in use
netstat -tulpn | grep 8000

# Verify music path exists
ls -la /mnt/user/Music
```

### **Bot Can't Connect to Discord**
1. Verify Discord token is correct
2. Check if Unraid has internet access
3. Ensure bot has proper permissions in Discord server

### **No Music Found**
1. Verify music share path is correct
2. Check file permissions on music directory
3. Run the library scan: `!scan` command in Discord

### **Web Interface Not Accessible**
1. Check if port 8000 is open
2. Verify container is running: `docker ps`
3. Check Unraid firewall settings

## 🚀 **Updates**

### **Automatic Updates (GitHub Registry)**
```bash
# Pull latest image and restart
docker-compose -f docker-compose.unraid.yml pull
docker-compose -f docker-compose.unraid.yml up -d
```

### **Manual Updates**
```bash
# Stop container
docker stop snowlander-bot

# Remove old container
docker rm snowlander-bot

# Pull latest image
docker pull ghcr.io/joeeuston-dev/snowlander:latest

# Restart with compose
docker-compose -f docker-compose.unraid.yml up -d
```

## 📊 **Performance Tuning**

### **Resource Limits**
The Unraid compose file includes sensible defaults:
- **Memory**: 1GB limit, 256MB reservation
- **CPU**: 0.5 CPU cores maximum

### **Adjusting for Large Libraries**
For libraries with 10,000+ tracks:
- Increase memory limit to 2GB
- Consider SSD cache for database storage

## 🎯 **Best Practices**

1. **Use GitHub Container Registry** for easy updates
2. **Store database on SSD** for better performance
3. **Use read-only music mounts** for safety
4. **Monitor container logs** for issues
5. **Backup database** periodically

## 🎉 **Success!**

Once deployed, you can:
- Access web interface at `http://your-unraid-ip:8000`
- Use Discord commands in your server
- Monitor bot status through the dashboard
- Browse and queue music through the web interface
