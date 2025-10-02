"""WebSocket connection manager for real-time updates."""

import json
from typing import List
from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Error sending message to WebSocket: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected WebSocket clients."""
        if not self.active_connections:
            return
        
        message_text = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                print(f"Error broadcasting to WebSocket: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_status_update(self, status_data: dict):
        """Broadcast bot status update."""
        await self.broadcast({
            "type": "status_update",
            "data": status_data
        })
    
    async def broadcast_track_update(self, track_data: dict):
        """Broadcast current track update."""
        await self.broadcast({
            "type": "track_update",
            "data": track_data
        })
    
    async def broadcast_queue_update(self, action: str, data: dict = None):
        """Broadcast queue update."""
        await self.broadcast({
            "type": "queue_update",
            "action": action,
            "data": data or {}
        })
