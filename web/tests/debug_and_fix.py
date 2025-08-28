#!/usr/bin/env python3
"""
Debug and Fix Script for TradingAgents Backend Issues
Identifies and fixes common backend startup and import errors
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackendDebugger:
    """Debug and fix backend issues"""
    
    def __init__(self, backend_path: str = "/Users/Gautam/TradingAgents/web/backend"):
        self.backend_path = Path(backend_path)
        self.app_path = self.backend_path / "app"
        
    def check_missing_imports(self):
        """Check for missing imports and fix them"""
        logger.info("🔍 Checking for missing imports...")
        
        # Check websocket.py for missing WebSocketStats
        websocket_models = self.app_path / "models" / "websocket.py"
        if websocket_models.exists():
            with open(websocket_models, 'r') as f:
                content = f.read()
                
            if "WebSocketStats" not in content:
                logger.info("➕ Adding missing WebSocketStats class")
                
                # Add WebSocketStats class
                stats_class = '''
class WebSocketStats(BaseModel):
    """WebSocket connection statistics"""
    total_connections: int = Field(default=0, description="Total connections")
    active_connections: int = Field(default=0, description="Active connections")
    messages_sent: int = Field(default=0, description="Messages sent")
    messages_received: int = Field(default=0, description="Messages received")
    uptime_seconds: float = Field(default=0.0, description="Uptime in seconds")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
'''
                
                # Insert before the last line
                lines = content.split('\n')
                lines.insert(-1, stats_class)
                
                with open(websocket_models, 'w') as f:
                    f.write('\n'.join(lines))
                    
                logger.info("✅ Added WebSocketStats class")
    
    def fix_import_errors(self):
        """Fix common import errors"""
        logger.info("🔧 Fixing import errors...")
        
        # Fix websocket router imports
        websocket_router = self.app_path / "routers" / "websocket.py"
        if websocket_router.exists():
            with open(websocket_router, 'r') as f:
                content = f.read()
            
            # Fix import path
            if "from app.models.websocket import" in content:
                content = content.replace(
                    "from app.models.websocket import",
                    "from ..models.websocket import"
                )
                
            # Fix service imports
            if "from app.services" in content:
                content = content.replace(
                    "from app.services",
                    "from ..services"
                )
                
            with open(websocket_router, 'w') as f:
                f.write(content)
                
            logger.info("✅ Fixed websocket router imports")
    
    def create_minimal_backend(self):
        """Create a minimal working backend for testing"""
        logger.info("🏗️ Creating minimal backend server...")
        
        minimal_server = self.backend_path / "minimal_server.py"
        
        server_code = '''#!/usr/bin/env python3
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
'''
        
        with open(minimal_server, 'w') as f:
            f.write(server_code)
            
        logger.info("✅ Created minimal backend server")
        return minimal_server
    
    def run_diagnostics(self):
        """Run comprehensive diagnostics"""
        logger.info("🩺 Running backend diagnostics...")
        
        issues = []
        
        # Check if backend directory exists
        if not self.backend_path.exists():
            issues.append("Backend directory not found")
        
        # Check if app directory exists
        if not self.app_path.exists():
            issues.append("App directory not found")
        
        # Check for main.py
        main_py = self.app_path / "main.py"
        if not main_py.exists():
            issues.append("main.py not found")
        
        # Check for models
        models_dir = self.app_path / "models"
        if not models_dir.exists():
            issues.append("Models directory not found")
        
        # Check for routers
        routers_dir = self.app_path / "routers"
        if not routers_dir.exists():
            issues.append("Routers directory not found")
        
        # Check for services
        services_dir = self.app_path / "services"
        if not services_dir.exists():
            issues.append("Services directory not found")
        
        if issues:
            logger.error(f"❌ Found {len(issues)} issues:")
            for issue in issues:
                logger.error(f"  - {issue}")
        else:
            logger.info("✅ No structural issues found")
        
        return issues
    
    def fix_all_issues(self):
        """Fix all identified issues"""
        logger.info("🔧 Starting comprehensive backend fix...")
        
        # Run diagnostics
        issues = self.run_diagnostics()
        
        # Fix missing imports
        self.check_missing_imports()
        self.fix_import_errors()
        
        # Create minimal server as fallback
        minimal_server = self.create_minimal_backend()
        
        logger.info("✅ Backend fixes completed")
        return minimal_server

def main():
    """Main execution"""
    print("🔧 TradingAgents Backend Debugger")
    print("=" * 40)
    
    debugger = BackendDebugger()
    minimal_server = debugger.fix_all_issues()
    
    print(f"\n🚀 Minimal server created at: {minimal_server}")
    print("Run with: python3 minimal_server.py")

if __name__ == "__main__":
    main()
