"""
WebSocket API Endpoints

This module provides WebSocket endpoints for real-time agent execution.
"""

from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json
import asyncio
from datetime import datetime

from database import get_db
from core.agent_engine import agent_engine
from core.logging import get_logger
from models.customer import Customer


router = APIRouter(tags=["WebSocket"])
logger = get_logger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.
    """
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            client_id: Unique client identifier
        """
        await websocket.accept()
        
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        
        self.active_connections[client_id].add(websocket)
        logger.info(f"WebSocket connected: {client_id}")
    
    def disconnect(self, websocket: WebSocket, client_id: str):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            client_id: Unique client identifier
        """
        if client_id in self.active_connections:
            self.active_connections[client_id].discard(websocket)
            
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        
        logger.info(f"WebSocket disconnected: {client_id}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """
        Send message to a specific client.
        
        Args:
            message: Message to send
            client_id: Client identifier
        """
        if client_id in self.active_connections:
            disconnected = set()
            
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send message: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.disconnect(connection, client_id)
    
    async def broadcast(self, message: dict):
        """
        Broadcast message to all connected clients.
        
        Args:
            message: Message to broadcast
        """
        for client_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, client_id)


manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time agent execution updates.
    
    Args:
        websocket: WebSocket connection
        client_id: Unique client identifier
        db: Database session
    """
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            
            if message_type == "execute_agent":
                # Execute agent and stream updates
                await handle_agent_execution(
                    websocket,
                    client_id,
                    data,
                    db
                )
            
            elif message_type == "ping":
                # Respond to ping
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.utcnow().isoformat()},
                    client_id
                )
            
            elif message_type == "subscribe":
                # Subscribe to updates
                await manager.send_personal_message(
                    {"type": "subscribed", "client_id": client_id},
                    client_id
                )
            
            else:
                await manager.send_personal_message(
                    {"type": "error", "message": f"Unknown message type: {message_type}"},
                    client_id
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        await manager.send_personal_message(
            {"type": "error", "message": str(e)},
            client_id
        )
        manager.disconnect(websocket, client_id)


async def handle_agent_execution(
    websocket: WebSocket,
    client_id: str,
    data: dict,
    db: Session
):
    """
    Handle agent execution with real-time updates.
    
    Args:
        websocket: WebSocket connection
        client_id: Client identifier
        data: Execution request data
        db: Database session
    """
    package_id = data.get("package_id")
    task = data.get("task")
    engine_type = data.get("engine_type", "crewai")
    
    if not package_id or not task:
        await manager.send_personal_message(
            {"type": "error", "message": "Missing package_id or task"},
            client_id
        )
        return
    
    # Send start notification
    await manager.send_personal_message(
        {
            "type": "execution_started",
            "package_id": package_id,
            "timestamp": datetime.utcnow().isoformat()
        },
        client_id
    )
    
    try:
        # Send progress updates
        await manager.send_personal_message(
            {
                "type": "execution_progress",
                "status": "initializing",
                "message": "Initializing agent..."
            },
            client_id
        )
        
        await asyncio.sleep(0.5)  # Simulate initialization
        
        await manager.send_personal_message(
            {
                "type": "execution_progress",
                "status": "running",
                "message": "Agent is processing your request..."
            },
            client_id
        )
        
        # Execute agent
        result = await agent_engine.execute(
            package_id=package_id,
            task_input={"task": task},
            engine_type=engine_type
        )
        
        # Send completion notification
        await manager.send_personal_message(
            {
                "type": "execution_completed",
                "package_id": package_id,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            },
            client_id
        )
    
    except Exception as e:
        logger.error(f"Agent execution error: {e}", exc_info=True)
        
        await manager.send_personal_message(
            {
                "type": "execution_failed",
                "package_id": package_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            },
            client_id
        )


@router.get("/ws/status")
async def websocket_status():
    """
    Get WebSocket connection status.
    
    Returns:
        Connection statistics
    """
    return {
        "active_connections": len(manager.active_connections),
        "total_clients": sum(len(conns) for conns in manager.active_connections.values()),
        "clients": list(manager.active_connections.keys())
    }

