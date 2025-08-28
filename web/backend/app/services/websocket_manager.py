#!/usr/bin/env python3
"""
WebSocket Manager Service
Thread-safe WebSocket connection management with session tracking and message broadcasting
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Set, Any, Optional, List
from collections import defaultdict
from fastapi import WebSocket, WebSocketDisconnect
from ..utils.performance import message_batcher, memory_manager, performance_monitor
from ..utils.security import rate_limiter, get_client_id
from ..models.websocket import (
    WebSocketMessage, AgentStatusUpdateMessage, MessageUpdateMessage, ToolCallMessage,
    ReportUpdateMessage, AnalysisCompleteMessage, AnalysisErrorMessage, HeartbeatMessage
)
logger = logging.getLogger(__name__)

class WebSocketConnection:
    """Individual WebSocket connection wrapper"""
    
    def __init__(self, websocket: WebSocket, session_id: str, connection_id: str):
        self.websocket = websocket
        self.session_id = session_id
        self.connection_id = connection_id
        self.connected_at = datetime.now()
        self.last_heartbeat = datetime.now()
        self.is_alive = True
        
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Send message to WebSocket connection"""
        try:
            await self.websocket.send_text(json.dumps(message, default=str))
            return True
        except Exception as e:
            logger.warning(f"Failed to send message to {self.connection_id}: {e}")
            self.is_alive = False
            return False
            
    async def send_heartbeat(self) -> bool:
        """Send heartbeat message"""
        heartbeat = HeartbeatMessage(session_id=self.session_id)
        return await self.send_message(heartbeat.dict())
        
    def update_heartbeat(self):
        """Update last heartbeat timestamp"""
        self.last_heartbeat = datetime.now()

class SessionManager:
    """Manages analysis sessions and their state"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_locks: Dict[str, asyncio.Lock] = {}
        
    def create_session(self, session_id: str, initial_data: Dict[str, Any]) -> None:
        """Create a new session"""
        self.sessions[session_id] = {
            "created_at": datetime.now(),
            "status": "pending",
            "data": initial_data,
            "last_activity": datetime.now()
        }
        self.session_locks[session_id] = asyncio.Lock()
        logger.info(f"Created session {session_id}")
        
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return self.sessions.get(session_id)
        
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> None:
        """Update session data"""
        if session_id in self.sessions:
            self.sessions[session_id]["data"].update(updates)
            self.sessions[session_id]["last_activity"] = datetime.now()
            
    def remove_session(self, session_id: str) -> None:
        """Remove session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if session_id in self.session_locks:
                del self.session_locks[session_id]
            logger.info(f"Removed session {session_id}")
            
    def cleanup_expired_sessions(self, timeout_minutes: int = 60) -> None:
        """Clean up expired sessions"""
        cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
        expired_sessions = [
            session_id for session_id, session_data in self.sessions.items()
            if session_data["last_activity"] < cutoff_time
        ]
        
        for session_id in expired_sessions:
            self.remove_session(session_id)
            logger.info(f"Cleaned up expired session {session_id}")

class WebSocketManager:
    """Thread-safe WebSocket connection manager"""
    
    def __init__(self, heartbeat_interval: int = 30, session_timeout: int = 60):
        # Connection management
        self.connections: Dict[str, WebSocketConnection] = {}
        self.session_connections: Dict[str, Set[str]] = defaultdict(set)
        self.connection_lock = asyncio.Lock()
        
        # Session management
        self.session_manager = SessionManager()
        
        # Configuration
        self.heartbeat_interval = heartbeat_interval
        self.session_timeout = session_timeout
        
        # Background tasks
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        
        logger.info("WebSocket Manager initialized")
        
    async def start(self):
        """Start background tasks"""
        if not self._running:
            self._running = True
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("WebSocket Manager background tasks started")
            
    async def stop(self):
        """Stop background tasks and close all connections"""
        self._running = False
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
                
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
                
        # Close all connections
        async with self.connection_lock:
            for connection in self.connections.values():
                try:
                    await connection.websocket.close()
                except Exception:
                    pass
            self.connections.clear()
            self.session_connections.clear()
            
        logger.info("WebSocket Manager stopped")
        
    async def connect(self, websocket: WebSocket, session_id: str) -> str:
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        connection = WebSocketConnection(websocket, session_id, connection_id)
        
        async with self.connection_lock:
            self.connections[connection_id] = connection
            self.session_connections[session_id].add(connection_id)
            
        # Send connection acknowledgment
        ack_message = {
            "type": "connection_ack",
            "session_id": session_id,
            "connection_id": connection_id,
            "message": f"WebSocket connection established for session {session_id}",
            "timestamp": datetime.now().isoformat()
        }
        await connection.send_message(ack_message)
        
        # Record performance metrics
        performance_monitor.record_websocket_connection(True)
        
        logger.info(f"WebSocket connected: {connection_id} for session {session_id}")
        return connection_id
        
    async def disconnect(self, connection_id: str):
        """Handle WebSocket disconnection"""
        async with self.connection_lock:
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                session_id = connection.session_id
                
                # Remove from connections
                del self.connections[connection_id]
                
                # Remove from session connections
                if session_id in self.session_connections:
                    self.session_connections[session_id].discard(connection_id)
                    if not self.session_connections[session_id]:
                        del self.session_connections[session_id]
                        
                logger.info(f"WebSocket disconnected: {connection_id} from session {session_id}")
                
                # Record performance metrics
                performance_monitor.record_websocket_connection(False)
                
    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any]) -> int:
        """Broadcast message to all connections in a session with performance optimizations"""
        if session_id not in self.session_connections:
            logger.warning(f"No connections found for session {session_id}")
            return 0
            
        # Store message in memory manager
        memory_manager.add_message(session_id, message)
        
        # Use message batcher for efficient transmission
        connection_ids = list(self.session_connections[session_id])
        successful_sends = 0
        failed_connections = []
        
        async def send_callback(msg):
            nonlocal successful_sends, failed_connections
            for connection_id in connection_ids:
                if connection_id in self.connections:
                    connection = self.connections[connection_id]
                    success = await connection.send_message(msg)
                    if success:
                        successful_sends += 1
                        performance_monitor.record_message_sent()
                    else:
                        failed_connections.append(connection_id)
        
        # Use message batcher for performance
        await message_batcher.add_message(session_id, message, send_callback)
        
        # Clean up failed connections
        if failed_connections:
            async with self.connection_lock:
                for connection_id in failed_connections:
                    await self.disconnect(connection_id)
                    
        return successful_sends
        
    async def broadcast_to_all(self, message: Dict[str, Any]) -> int:
        """Broadcast message to all active connections"""
        connection_ids = list(self.connections.keys())
        successful_sends = 0
        failed_connections = []
        
        for connection_id in connection_ids:
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                success = await connection.send_message(message)
                if success:
                    successful_sends += 1
                else:
                    failed_connections.append(connection_id)
                    
        # Clean up failed connections
        if failed_connections:
            async with self.connection_lock:
                for connection_id in failed_connections:
                    await self.disconnect(connection_id)
                    
        return successful_sends
        
    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """Send message to specific connection"""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            success = await connection.send_message(message)
            if not success:
                await self.disconnect(connection_id)
            return success
        return False
        
    def get_session_connection_count(self, session_id: str) -> int:
        """Get number of active connections for a session"""
        return len(self.session_connections.get(session_id, set()))
        
    def get_total_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.connections)
        
    def get_session_list(self) -> List[str]:
        """Get list of active sessions"""
        return list(self.session_connections.keys())
        
    async def handle_websocket_communication(self, websocket: WebSocket, session_id: str):
        """Handle WebSocket communication lifecycle"""
        connection_id = None
        try:
            # Connect
            connection_id = await self.connect(websocket, session_id)
            
            # Listen for messages (mainly for heartbeat responses)
            while True:
                try:
                    # Wait for message with timeout
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                    
                    # Update heartbeat for this connection
                    if connection_id in self.connections:
                        self.connections[connection_id].update_heartbeat()
                        
                    # Handle client messages if needed
                    try:
                        client_message = json.loads(data)
                        await self._handle_client_message(connection_id, client_message)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON from client {connection_id}")
                        
                except asyncio.TimeoutError:
                    # No message received, continue (heartbeat will handle dead connections)
                    continue
                except WebSocketDisconnect:
                    break
                    
        except Exception as e:
            logger.error(f"WebSocket communication error: {e}")
        finally:
            if connection_id:
                await self.disconnect(connection_id)
                
    async def _handle_client_message(self, connection_id: str, message: Dict[str, Any]):
        """Handle messages from client"""
        message_type = message.get("type")
        
        if message_type == "heartbeat_response":
            # Client responded to heartbeat
            if connection_id in self.connections:
                self.connections[connection_id].update_heartbeat()
        elif message_type == "ping":
            # Client ping, send pong
            pong_message = {"type": "pong", "timestamp": datetime.now().isoformat()}
            await self.send_to_connection(connection_id, pong_message)
        else:
            logger.debug(f"Unhandled client message type: {message_type}")
            
    async def _heartbeat_loop(self):
        """Background task to send heartbeats and detect dead connections"""
        while self._running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                current_time = datetime.now()
                dead_connections = []
                
                # Check all connections
                for connection_id, connection in self.connections.items():
                    time_since_heartbeat = current_time - connection.last_heartbeat
                    
                    if time_since_heartbeat.total_seconds() > self.heartbeat_interval * 2:
                        # Connection is dead
                        dead_connections.append(connection_id)
                    else:
                        # Send heartbeat
                        await connection.send_heartbeat()
                        
                # Clean up dead connections
                for connection_id in dead_connections:
                    logger.info(f"Removing dead connection: {connection_id}")
                    await self.disconnect(connection_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
                
    async def _cleanup_loop(self):
        """Background task to clean up expired sessions"""
        while self._running:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                self.session_manager.cleanup_expired_sessions(self.session_timeout)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")

# Global WebSocket manager instance
websocket_manager = WebSocketManager()

async def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance"""
    if not websocket_manager._running:
        await websocket_manager.start()
    return websocket_manager
