#!/usr/bin/env python3
"""
WebSocket Router
WebSocket endpoints for real-time communication
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from ..models.websocket import (
    WebSocketMessage, WebSocketMessageType, WebSocketStats,
    AgentStatusMessage, AnalysisMessage, ToolCallMessage, ReportMessage, ErrorMessage
)
from ..services.websocket_manager import WebSocketManager
from ..services.session_manager import get_session_manager

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication"""
    websocket_manager = await get_websocket_manager()
    session_manager = await get_session_manager()
    
    # Validate session exists
    session = session_manager.get_session(session_id)
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return
    
    try:
        # Handle WebSocket communication
        await websocket_manager.handle_websocket_communication(websocket, session_id)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass

@router.get("/{session_id}/connections")
async def get_session_connections(session_id: str):
    """Get number of active WebSocket connections for a session"""
    try:
        websocket_manager = await get_websocket_manager()
        connection_count = websocket_manager.get_session_connection_count(session_id)
        
        return {
            "session_id": session_id,
            "active_connections": connection_count
        }
    except Exception as e:
        logger.error(f"Error getting connections for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get connection count")

@router.get("/stats")
async def get_websocket_stats():
    """Get WebSocket statistics"""
    try:
        websocket_manager = await get_websocket_manager()
        
        return {
            "total_connections": websocket_manager.get_total_connection_count(),
            "active_sessions": len(websocket_manager.get_session_list()),
            "session_list": websocket_manager.get_session_list()
        }
    except Exception as e:
        logger.error(f"Error getting WebSocket stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get WebSocket statistics")
