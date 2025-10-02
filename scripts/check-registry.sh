#!/bin/bash
# Script to check GitHub Container Registry for SNOWLANDER images

echo "🔍 Checking GitHub Container Registry for SNOWLANDER images..."
echo ""

# Check if images are available
echo "📦 Available images and tags:"
echo ""

# Try to get image tags
echo "🏷️  Latest tags:"
docker manifest inspect ghcr.io/joeeuston-dev/snowlander:latest > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ ghcr.io/joeeuston-dev/snowlander:latest - Available"
    
    # Get image size and details
    echo "📊 Image details:"
    docker images ghcr.io/joeeuston-dev/snowlander:latest --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" 2>/dev/null || echo "   (Pull image to see size details)"
else
    echo "❌ ghcr.io/joeeuston-dev/snowlander:latest - Not available yet"
fi

echo ""
docker manifest inspect ghcr.io/joeeuston-dev/snowlander:alpine > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ ghcr.io/joeeuston-dev/snowlander:alpine - Available"
else
    echo "❌ ghcr.io/joeeuston-dev/snowlander:alpine - Not available yet"
fi

echo ""
echo "🚀 To pull images:"
echo "   docker pull ghcr.io/joeeuston-dev/snowlander:latest"
echo "   docker pull ghcr.io/joeeuston-dev/snowlander:alpine"

echo ""
echo "📋 For Unraid deployment:"
echo "   Repository: ghcr.io/joeeuston-dev/snowlander:latest"
echo "   or Alpine:  ghcr.io/joeeuston-dev/snowlander:alpine"
