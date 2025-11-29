from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import asyncio
from app.auth import decode_access_token

class ConnectionManager:
    def __init__(self):
        # Store connections by user_id
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Add a lock for thread-safe operations
        self.lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        async with self.lock:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(websocket)
        print(f"WebSocket connected for user {user_id}. Total connections: {len(self.active_connections.get(user_id, set()))}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            print(f"WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, message: dict, user_id: int):
        print(f"Attempting to send message to user {user_id}: {message}")
        if user_id in self.active_connections:
            connections_to_remove = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                    print(f"Successfully sent message to user {user_id}")
                except Exception as e:
                    print(f"Failed to send message to user {user_id}: {e}")
                    connections_to_remove.append(connection)
            
            # Remove broken connections
            if connections_to_remove:
                async with self.lock:
                    for connection in connections_to_remove:
                        self.active_connections[user_id].discard(connection)
                        if not self.active_connections[user_id]:
                            del self.active_connections[user_id]
        else:
            print(f"No active connections for user {user_id}")

    async def broadcast(self, message: dict):
        print(f"Broadcasting message to all users: {message}")
        users_to_remove = []
        for user_id, connections in self.active_connections.items():
            connections_to_remove = []
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Failed to broadcast to user {user_id}: {e}")
                    connections_to_remove.append(connection)
            
            # Remove broken connections
            if connections_to_remove:
                async with self.lock:
                    for connection in connections_to_remove:
                        self.active_connections[user_id].discard(connection)
                        if not self.active_connections[user_id]:
                            users_to_remove.append(user_id)
        
        # Remove users with no connections
        if users_to_remove:
            async with self.lock:
                for user_id in users_to_remove:
                    if user_id in self.active_connections:
                        del self.active_connections[user_id]

manager = ConnectionManager()