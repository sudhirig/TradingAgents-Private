#!/usr/bin/env python3
"""
Analysis Data Models
Pydantic models for analysis requests, responses, and session management
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum

class AnalystType(str, Enum):
    """Available analyst types"""
    MARKET_ANALYST = "Market Analyst"
    SOCIAL_ANALYST = "Social Analyst"
    NEWS_ANALYST = "News Analyst"
    FUNDAMENTALS_ANALYST = "Fundamentals Analyst"
    BULL_RESEARCHER = "Bull Researcher"
    BEAR_RESEARCHER = "Bear Researcher"
    RESEARCH_MANAGER = "Research Manager"
    TRADER = "Trader"
    RISKY_ANALYST = "Risky Analyst"
    NEUTRAL_ANALYST = "Neutral Analyst"
    SAFE_ANALYST = "Safe Analyst"
    PORTFOLIO_MANAGER = "Portfolio Manager"

class AgentStatus(str, Enum):
    """Agent execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisStatus(str, Enum):
    """Analysis session status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"

class LLMConfig(BaseModel):
    """LLM configuration"""
    provider: LLMProvider = Field(..., description="LLM provider")
    model: str = Field(..., description="Model name")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature for response generation")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens to generate")
    
    @validator('model')
    def validate_model(cls, v, values):
        """Validate model name based on provider"""
        provider = values.get('provider')
        
        valid_models = {
            LLMProvider.OPENAI: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
            LLMProvider.ANTHROPIC: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
            LLMProvider.GROQ: ['llama2-70b-4096', 'mixtral-8x7b-32768']
        }
        
        if provider and v not in valid_models.get(provider, []):
            raise ValueError(f"Invalid model '{v}' for provider '{provider}'")
        
        return v

class AnalysisRequest(BaseModel):
    """Request to start a new analysis"""
    ticker: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    trade_date: str = Field(..., description="Trade date in YYYY-MM-DD format")
    selected_analysts: List[AnalystType] = Field(..., min_items=1, description="List of analysts to include")
    research_depth: int = Field(1, ge=1, le=5, description="Research depth (1-5)")
    llm_config: LLMConfig = Field(..., description="LLM configuration")
    
    @validator('ticker')
    def validate_ticker(cls, v):
        """Validate ticker format"""
        return v.upper().strip()
    
    @validator('trade_date')
    def validate_trade_date(cls, v):
        """Validate trade date format"""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError("Trade date must be in YYYY-MM-DD format")
    
    @validator('selected_analysts')
    def validate_analysts(cls, v):
        """Validate analyst selection"""
        if not v:
            raise ValueError("At least one analyst must be selected")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_analysts = []
        for analyst in v:
            if analyst not in seen:
                seen.add(analyst)
                unique_analysts.append(analyst)
        
        return unique_analysts

class AnalysisResponse(BaseModel):
    """Response when starting an analysis"""
    session_id: str = Field(..., description="Unique session identifier")
    status: AnalysisStatus = Field(..., description="Current analysis status")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(default_factory=datetime.now, description="Session creation timestamp")

class AgentStatusUpdate(BaseModel):
    """Agent status update"""
    agent: AnalystType = Field(..., description="Agent name")
    status: AgentStatus = Field(..., description="Agent status")
    start_time: Optional[datetime] = Field(None, description="Agent start time")
    end_time: Optional[datetime] = Field(None, description="Agent completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")

class AnalysisSessionStatus(BaseModel):
    """Current analysis session status"""
    session_id: str = Field(..., description="Session identifier")
    status: AnalysisStatus = Field(..., description="Overall analysis status")
    progress: float = Field(0.0, ge=0.0, le=100.0, description="Progress percentage")
    agent_statuses: Dict[str, AgentStatus] = Field(default_factory=dict, description="Individual agent statuses")
    current_agent: Optional[str] = Field(None, description="Currently active agent")
    created_at: datetime = Field(..., description="Session creation time")
    started_at: Optional[datetime] = Field(None, description="Analysis start time")
    completed_at: Optional[datetime] = Field(None, description="Analysis completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")

class ReportSection(BaseModel):
    """Individual report section"""
    section_name: str = Field(..., description="Report section name")
    content: Optional[str] = Field(None, description="Report content in markdown")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    agent: Optional[str] = Field(None, description="Agent that generated this section")

class AnalysisReports(BaseModel):
    """Complete analysis reports"""
    session_id: str = Field(..., description="Session identifier")
    reports: Dict[str, Optional[str]] = Field(default_factory=dict, description="Report sections")
    final_trade_decision: Optional[str] = Field(None, description="Final trading decision")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

class AnalysisSession(BaseModel):
    """Complete analysis session data"""
    session_id: str = Field(..., description="Session identifier")
    request: AnalysisRequest = Field(..., description="Original analysis request")
    status: AnalysisStatus = Field(..., description="Current status")
    progress: float = Field(0.0, ge=0.0, le=100.0, description="Progress percentage")
    agent_statuses: Dict[str, AgentStatus] = Field(default_factory=dict, description="Agent statuses")
    reports: Dict[str, Optional[str]] = Field(default_factory=dict, description="Report sections")
    created_at: datetime = Field(..., description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

# Configuration models
class AnalystInfo(BaseModel):
    """Information about an analyst"""
    name: AnalystType = Field(..., description="Analyst name")
    description: str = Field(..., description="Analyst description")
    team: str = Field(..., description="Team name")
    color: str = Field(..., description="UI color code")

class ConfigResponse(BaseModel):
    """Configuration response"""
    analysts: List[AnalystInfo] = Field(..., description="Available analysts")
    llm_providers: List[LLMProvider] = Field(..., description="Available LLM providers")
    models: Dict[str, List[str]] = Field(..., description="Available models per provider")
    max_research_depth: int = Field(5, description="Maximum research depth")
    default_config: Dict[str, Any] = Field(..., description="Default configuration values")
