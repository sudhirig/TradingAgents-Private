#!/usr/bin/env python3
"""
Minimal TradingAgents Backend Server for Testing
Provides basic endpoints without complex dependencies
"""

import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
import uuid

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

app = FastAPI(
    title="TradingAgents Minimal API",
    description="Minimal backend for testing",
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

# Data models
class AnalysisRequest(BaseModel):
    ticker: str
    analysis_date: str
    analysts: List[str] = []
    research_depth: int = 3
    llm_config: Dict[str, Any] = {}

class AnalysisResponse(BaseModel):
    session_id: str
    status: str
    message: str

# Mock data
ANALYSTS = [
    "Market Analyst",
    "Social Analyst", 
    "News Analyst",
    "Fundamentals Analyst"
]

LLM_PROVIDERS = [
    {"name": "OpenAI", "models": ["gpt-4o-mini", "o1"]},
    {"name": "Anthropic", "models": ["claude-3-5-haiku-latest", "claude-sonnet-4-0"]},
    {"name": "Groq", "models": ["llama-3.1-70b-versatile"]}
]

# Routes
@app.get("/")
async def root():
    return {"message": "TradingAgents Minimal API", "status": "running"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "TradingAgents Minimal Backend",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/config/analysts")
async def get_analysts():
    return ANALYSTS

@app.get("/api/config/llm-providers")
async def get_llm_providers():
    return LLM_PROVIDERS

@app.get("/api/config/models/{provider}")
async def get_models(provider: str):
    for p in LLM_PROVIDERS:
        if p["name"].lower() == provider.lower():
            return p["models"]
    raise HTTPException(status_code=404, detail="Provider not found")

@app.post("/api/analysis/start", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest):
    session_id = str(uuid.uuid4())
    
    # Basic validation
    if not request.ticker:
        raise HTTPException(status_code=422, detail="Ticker is required")
    
    if not request.analysts:
        raise HTTPException(status_code=422, detail="At least one analyst is required")
    
    return AnalysisResponse(
        session_id=session_id,
        status="started",
        message=f"Analysis started for {request.ticker}"
    )

@app.get("/api/analysis/{session_id}/status")
async def get_analysis_status(session_id: str):
    return {
        "session_id": session_id,
        "status": "running",
        "progress": 0.5,
        "message": "Analysis in progress"
    }

if __name__ == "__main__":
    uvicorn.run(
        "minimal_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
