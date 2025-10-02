# GitHub Container Registry Guide

## 🎉 **SNOWLANDER Images Are Live!**

Your SNOWLANDER Docker images are now available on GitHub Container Registry!

## 📦 **Available Images**

### **Default (Optimized)**
- **Repository**: `ghcr.io/joeeuston-dev/snowlander:latest`
- **Size**: ~250MB
- **Base**: Debian slim with optimizations
- **Best for**: Production deployments with full compatibility

### **Alpine (Lightweight)**
- **Repository**: `ghcr.io/joeeuston-dev/snowlander:alpine`
- **Size**: ~290MB (compressed layers make it efficient)
- **Base**: Alpine Linux
- **Best for**: Resource-constrained environments like Unraid

## 🔍 **How to Check Registry**

### **Browse on GitHub**
Visit: https://github.com/joeeuston-dev/snowlander/pkgs/container/snowlander

### **Command Line Check**
```bash
# Run the included script
./scripts/check-registry.sh

# Or manually check
docker manifest inspect ghcr.io/joeeuston-dev/snowlander:latest
docker manifest inspect ghcr.io/joeeuston-dev/snowlander:alpine
```

### **Pull Images**
```bash
# Default optimized version
docker pull ghcr.io/joeeuston-dev/snowlander:latest

# Lightweight Alpine version  
docker pull ghcr.io/joeeuston-dev/snowlander:alpine

# Specific commit (auto-tagged)
docker pull ghcr.io/joeeuston-dev/snowlander:alpine-464d5db
```

## 🚀 **Updated Unraid Installation**

### **Option 1: Simple Docker Run**
```bash
# Quick start with Alpine (recommended for Unraid)
docker run -d \
  --name snowlander-bot \
  -p 8000:8000 \
  -v /mnt/user/Music:/app/data/music:ro \
  -v /mnt/user/appdata/snowlander:/app/data/database \
  -e DISCORD_TOKEN=your_bot_token_here \
  ghcr.io/joeeuston-dev/snowlander:alpine
```

### **Option 2: Docker Compose (Recommended)**
```bash
# Download and use the Unraid compose file
wget https://raw.githubusercontent.com/joeeuston-dev/snowlander/main/docker-compose.unraid.yml
# Edit with your settings
docker-compose -f docker-compose.unraid.yml up -d
```

### **Option 3: Unraid Template**
Use this in your Unraid Docker template:
- **Repository**: `ghcr.io/joeeuston-dev/snowlander:alpine`
- **Tag**: `alpine` (or leave empty for latest)

## ⚡ **Performance Comparison**

| Image | Size | Memory | Use Case |
|-------|------|--------|----------|
| `:latest` | ~250MB | ~150MB | Production with full features |
| `:alpine` | ~290MB | ~120MB | Lightweight for constrained systems |

*Note: Alpine appears larger due to layer compression differences but uses less runtime memory.*

## 🔄 **Automatic Updates**

### **How It Works**
1. **Every push** to main branch triggers GitHub Actions
2. **Builds both** `:latest` and `:alpine` variants
3. **Pushes to** GitHub Container Registry
4. **Available immediately** for deployment

### **Update Your Container**
```bash
# Pull latest image
docker pull ghcr.io/joeeuston-dev/snowlander:alpine

# Restart container
docker-compose -f docker-compose.unraid.yml up -d
```

## 🎯 **Registry Benefits**

### **✅ Advantages**
- **No build time** - Pre-built images ready to download
- **Automatic updates** - New images on every code push
- **Multiple variants** - Choose optimized vs lightweight
- **Version tags** - Access specific commits if needed
- **Fast downloads** - GitHub's global CDN

### **🆚 vs Building Locally**
- **Speed**: 2-3 minutes download vs 10-15 minutes build
- **Resources**: No build CPU/memory usage on your server
- **Consistency**: Same image everywhere
- **Convenience**: One command deployment

## 📋 **Recommended for Unraid**

### **Best Choice: Alpine Variant**
```bash
# Repository for Unraid
ghcr.io/joeeuston-dev/snowlander:alpine
```

**Why Alpine for Unraid:**
- ✅ Smaller memory footprint
- ✅ Faster startup
- ✅ All features work perfectly
- ✅ Better for shared server resources

## 🎉 **You're Ready!**

Your SNOWLANDER bot can now be deployed on Unraid with a single command using the GitHub Container Registry. No more building from source - just pull and run!

Access your registry at: https://github.com/joeeuston-dev/snowlander/pkgs/container/snowlander
