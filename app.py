from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from typing import Optional
import uvicorn

# Import the trading agents functionality
import load_env  # Load .env file
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Initialize FastAPI app
app = FastAPI(
    title="TradingAgents API",
    description="Multi-agent trading analysis platform",
    version="1.0.0"
)

# CORS configuration for Replit
origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "https://*.repl.co",
    "https://*.replit.dev",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AnalysisRequest(BaseModel):
    ticker: str
    date: str
    analysts: Optional[str] = "all"
    research_depth: Optional[str] = "standard"

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

# Initialize TradingAgents with config
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"
config["backend_url"] = "https://api.openai.com/v1"
config["deep_think_llm"] = "gpt-4o"
config["quick_think_llm"] = "gpt-4o-mini"
config["max_debate_rounds"] = 1
config["online_tools"] = True

ta = TradingAgentsGraph(debug=True, config=config)

# Routes
@app.get("/", response_model=dict)
async def root():
    return {
        "message": "TradingAgents API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="tradingagents",
        version="1.0.0"
    )

@app.post("/api/analysis/start")
async def start_analysis(request: AnalysisRequest):
    try:
        # Run the trading agents analysis
        _, decision = ta.propagate(request.ticker, request.date)
        
        return {
            "success": True,
            "ticker": request.ticker,
            "date": request.date,
            "decision": decision,
            "message": "Analysis completed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/config/analysts")
async def get_analysts():
    return {
        "analysts": [
            "Market Analyst",
            "Social Analyst", 
            "News Analyst",
            "Fundamentals Analyst",
            "Bull Researcher",
            "Bear Researcher",
            "Research Manager",
            "Trader",
            "Risky Analyst",
            "Neutral Analyst",
            "Safe Analyst",
            "Portfolio Manager"
        ]
    }

@app.get("/api/config/llm-providers")
async def get_llm_providers():
    return {
        "providers": ["openai", "anthropic", "groq"]
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
