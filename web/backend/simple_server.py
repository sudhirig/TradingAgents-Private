#!/usr/bin/env python3
"""
Simple FastAPI server for TradingAgents Web Backend
Minimal setup to get the real WebSocket implementation running
"""

import os
import sys
import logging
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path
sys.path.append('/Users/Gautam/TradingAgents')

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TradingAgents Web API",
    description="Real-time financial analysis with multi-agent LLM system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple data models
class AnalystConfig(BaseModel):
    id: str
    name: str
    description: str
    team: str
    capabilities: List[str]
    enabled: bool = True

class LLMModel(BaseModel):
    id: str
    display_name: str
    context_window: int
    max_tokens: int

class LLMProvider(BaseModel):
    id: str
    display_name: str
    models: List[LLMModel]
    enabled: bool = True

class AnalysisRequest(BaseModel):
    company: str
    trade_date: str
    selected_analysts: List[str]
    llm_provider: str
    llm_model: str
    research_depth: str

# Mock data
ANALYSTS = [
    AnalystConfig(
        id="market-analyst",
        name="Market Analyst",
        description="Analyzes market trends and price movements",
        team="Analysis Team",
        capabilities=["market_analysis", "technical_analysis"]
    ),
    AnalystConfig(
        id="social-analyst", 
        name="Social Analyst",
        description="Analyzes social sentiment and news",
        team="Analysis Team",
        capabilities=["sentiment_analysis", "social_media"]
    ),
    AnalystConfig(
        id="fundamentals-analyst",
        name="Fundamentals Analyst", 
        description="Analyzes company fundamentals",
        team="Analysis Team",
        capabilities=["fundamental_analysis", "financial_metrics"]
    )
]

LLM_PROVIDERS = [
    LLMProvider(
        id="openai",
        display_name="OpenAI",
        models=[
            LLMModel(id="gpt-4", display_name="GPT-4", context_window=8192, max_tokens=4096),
            LLMModel(id="gpt-3.5-turbo", display_name="GPT-3.5 Turbo", context_window=4096, max_tokens=2048)
        ]
    ),
    LLMProvider(
        id="anthropic", 
        display_name="Anthropic",
        models=[
            LLMModel(id="claude-3", display_name="Claude 3", context_window=8192, max_tokens=4096)
        ]
    )
]

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {e}")
                self.disconnect(session_id)

    async def broadcast(self, message: dict):
        for session_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to {session_id}: {e}")

manager = ConnectionManager()

# API Endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "TradingAgents Web Backend", 
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/config/analysts")
async def get_analysts():
    return ANALYSTS

@app.get("/api/config/llm-providers") 
async def get_llm_providers():
    return LLM_PROVIDERS

@app.post("/api/analysis/start")
async def start_analysis(request: AnalysisRequest):
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Send initial status
    await manager.send_message(session_id, {
        "type": "session_started",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "company": request.company,
            "analysts": request.selected_analysts,
            "status": "started"
        }
    })
    
    return {"session_id": session_id, "status": "started"}

@app.get("/api/websocket/stats")
async def get_websocket_stats():
    return {
        "active_connections": len(manager.active_connections),
        "total_messages": 0
    }

# WebSocket endpoint
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "data": {"message": "WebSocket connected successfully"}
        })
        
        # Demo: Send some sample agent status updates
        import asyncio
        agents = ["Market Analyst", "Social Analyst", "Fundamentals Analyst"]
        
        for i, agent in enumerate(agents):
            await asyncio.sleep(2)  # Wait 2 seconds between updates
            
            # Send agent status update
            await websocket.send_json({
                "type": "agent_status",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "agent_name": agent,
                    "status": "running",
                    "progress": (i + 1) * 30,
                    "current_task": f"Analyzing {agent.lower()} data..."
                }
            })
            
            # Send sample message
            await websocket.send_json({
                "type": "message",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "agent": agent,
                    "message_type": "info",
                    "content": f"{agent} is processing market data for analysis...",
                    "timestamp": datetime.now().isoformat()
                }
            })
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                # Echo back any received messages
                await websocket.send_json({
                    "type": "echo",
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "data": {"received": data}
                })
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {e}")
        manager.disconnect(session_id)

if __name__ == "__main__":
    logger.info("🚀 Starting TradingAgents Simple Backend Server")
    logger.info("📚 API documentation available at http://localhost:8003/docs")
    
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )
