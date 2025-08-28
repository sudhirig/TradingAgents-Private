#!/usr/bin/env python3
"""
Configuration Data Models
Pydantic models for application configuration and settings
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from .analysis import AnalystType, LLMProvider

class AnalystTeamInfo(BaseModel):
    """Information about analyst teams"""
    name: str = Field(..., description="Team name")
    description: str = Field(..., description="Team description")
    color: str = Field(..., description="Team color for UI")
    analysts: List[AnalystType] = Field(..., description="Analysts in this team")

class AnalystConfiguration(BaseModel):
    """Individual analyst configuration"""
    name: AnalystType = Field(..., description="Analyst name")
    display_name: str = Field(..., description="Display name for UI")
    description: str = Field(..., description="Analyst description")
    team: str = Field(..., description="Team name")
    color: str = Field(..., description="Color for UI")
    icon: Optional[str] = Field(None, description="Icon name")
    enabled: bool = Field(True, description="Whether analyst is enabled")
    dependencies: List[AnalystType] = Field(default_factory=list, description="Required analysts")

class LLMModelInfo(BaseModel):
    """Information about LLM models"""
    name: str = Field(..., description="Model name")
    display_name: str = Field(..., description="Display name")
    description: str = Field(..., description="Model description")
    max_tokens: int = Field(..., description="Maximum context tokens")
    cost_per_token: Optional[float] = Field(None, description="Cost per token")
    recommended: bool = Field(False, description="Whether this is a recommended model")

class LLMProviderConfig(BaseModel):
    """LLM provider configuration"""
    name: LLMProvider = Field(..., description="Provider name")
    display_name: str = Field(..., description="Display name")
    description: str = Field(..., description="Provider description")
    models: List[LLMModelInfo] = Field(..., description="Available models")
    api_key_required: bool = Field(True, description="Whether API key is required")
    enabled: bool = Field(True, description="Whether provider is enabled")

class SystemConfiguration(BaseModel):
    """System-wide configuration"""
    max_concurrent_sessions: int = Field(10, description="Maximum concurrent analysis sessions")
    session_timeout_minutes: int = Field(60, description="Session timeout in minutes")
    websocket_heartbeat_interval: int = Field(30, description="WebSocket heartbeat interval in seconds")
    max_message_history: int = Field(1000, description="Maximum messages to keep in history")
    enable_rate_limiting: bool = Field(True, description="Whether to enable rate limiting")
    rate_limit_requests_per_minute: int = Field(60, description="Rate limit per minute")
    log_level: str = Field("INFO", description="Logging level")

class UIConfiguration(BaseModel):
    """UI configuration settings"""
    theme: str = Field("light", description="Default theme")
    auto_scroll_messages: bool = Field(True, description="Auto-scroll message feed")
    show_timestamps: bool = Field(True, description="Show timestamps in UI")
    animation_duration: int = Field(300, description="Animation duration in milliseconds")
    refresh_interval: int = Field(1000, description="UI refresh interval in milliseconds")
    max_report_length: int = Field(50000, description="Maximum report length to display")

class ApplicationConfig(BaseModel):
    """Complete application configuration"""
    analysts: List[AnalystConfiguration] = Field(..., description="Analyst configurations")
    teams: List[AnalystTeamInfo] = Field(..., description="Team configurations")
    llm_providers: List[LLMProviderConfig] = Field(..., description="LLM provider configurations")
    system: SystemConfiguration = Field(default_factory=SystemConfiguration, description="System configuration")
    ui: UIConfiguration = Field(default_factory=UIConfiguration, description="UI configuration")
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True

class AnalystInfo(BaseModel):
    """Simplified analyst info for API responses"""
    name: str = Field(..., description="Analyst name")
    description: str = Field(..., description="Analyst description")
    team: str = Field(..., description="Team name")
    color: str = Field(..., description="Color for UI")

class ConfigResponse(BaseModel):
    """Configuration API response"""
    analysts: List[AnalystInfo] = Field(..., description="Available analysts")
    llm_providers: List[str] = Field(..., description="Available LLM providers")
    models: Dict[str, List[str]] = Field(..., description="Models by provider")
    max_research_depth: int = Field(5, description="Maximum research depth")
    default_config: Dict[str, Any] = Field(..., description="Default configuration values")

# Default configurations
DEFAULT_ANALYST_TEAMS = [
    AnalystTeamInfo(
        name="Analysis Team",
        description="Market and fundamental analysis specialists",
        color="#3B82F6",  # Blue
        analysts=[
            AnalystType.MARKET_ANALYST,
            AnalystType.SOCIAL_ANALYST,
            AnalystType.NEWS_ANALYST,
            AnalystType.FUNDAMENTALS_ANALYST
        ]
    ),
    AnalystTeamInfo(
        name="Research Team",
        description="Investment research and strategy development",
        color="#8B5CF6",  # Purple
        analysts=[
            AnalystType.BULL_RESEARCHER,
            AnalystType.BEAR_RESEARCHER,
            AnalystType.RESEARCH_MANAGER
        ]
    ),
    AnalystTeamInfo(
        name="Trading Team",
        description="Trade execution and strategy implementation",
        color="#10B981",  # Green
        analysts=[AnalystType.TRADER]
    ),
    AnalystTeamInfo(
        name="Risk Management",
        description="Risk assessment and portfolio protection",
        color="#EF4444",  # Red
        analysts=[
            AnalystType.RISKY_ANALYST,
            AnalystType.NEUTRAL_ANALYST,
            AnalystType.SAFE_ANALYST
        ]
    ),
    AnalystTeamInfo(
        name="Portfolio Management",
        description="Portfolio optimization and final decisions",
        color="#F59E0B",  # Amber/Gold
        analysts=[AnalystType.PORTFOLIO_MANAGER]
    )
]

DEFAULT_ANALYST_CONFIGS = [
    AnalystConfiguration(
        name=AnalystType.MARKET_ANALYST,
        display_name="Market Analyst",
        description="Analyzes market trends, technical indicators, and price movements",
        team="Analysis Team",
        color="#3B82F6",
        icon="chart-line",
        dependencies=[]
    ),
    AnalystConfiguration(
        name=AnalystType.SOCIAL_ANALYST,
        display_name="Social Media Analyst",
        description="Monitors social sentiment and public opinion",
        team="Analysis Team",
        color="#3B82F6",
        icon="users",
        dependencies=[]
    ),
    AnalystConfiguration(
        name=AnalystType.NEWS_ANALYST,
        display_name="News Analyst",
        description="Analyzes news events and their market impact",
        team="Analysis Team",
        color="#3B82F6",
        icon="newspaper",
        dependencies=[]
    ),
    AnalystConfiguration(
        name=AnalystType.FUNDAMENTALS_ANALYST,
        display_name="Fundamentals Analyst",
        description="Evaluates company financials and business fundamentals",
        team="Analysis Team",
        color="#3B82F6",
        icon="building-office",
        dependencies=[]
    ),
    AnalystConfiguration(
        name=AnalystType.BULL_RESEARCHER,
        display_name="Bull Researcher",
        description="Develops bullish investment arguments and strategies",
        team="Research Team",
        color="#8B5CF6",
        icon="trending-up",
        dependencies=[AnalystType.MARKET_ANALYST, AnalystType.FUNDAMENTALS_ANALYST]
    ),
    AnalystConfiguration(
        name=AnalystType.BEAR_RESEARCHER,
        display_name="Bear Researcher",
        description="Develops bearish investment arguments and risk scenarios",
        team="Research Team",
        color="#8B5CF6",
        icon="trending-down",
        dependencies=[AnalystType.MARKET_ANALYST, AnalystType.FUNDAMENTALS_ANALYST]
    ),
    AnalystConfiguration(
        name=AnalystType.RESEARCH_MANAGER,
        display_name="Research Manager",
        description="Synthesizes research and manages investment debates",
        team="Research Team",
        color="#8B5CF6",
        icon="user-group",
        dependencies=[AnalystType.BULL_RESEARCHER, AnalystType.BEAR_RESEARCHER]
    ),
    AnalystConfiguration(
        name=AnalystType.TRADER,
        display_name="Trader",
        description="Develops trading strategies and execution plans",
        team="Trading Team",
        color="#10B981",
        icon="currency-dollar",
        dependencies=[AnalystType.RESEARCH_MANAGER]
    ),
    AnalystConfiguration(
        name=AnalystType.RISKY_ANALYST,
        display_name="Risk-Seeking Analyst",
        description="Evaluates high-risk, high-reward scenarios",
        team="Risk Management",
        color="#EF4444",
        icon="fire",
        dependencies=[AnalystType.TRADER]
    ),
    AnalystConfiguration(
        name=AnalystType.NEUTRAL_ANALYST,
        display_name="Neutral Risk Analyst",
        description="Provides balanced risk assessment",
        team="Risk Management",
        color="#EF4444",
        icon="scale",
        dependencies=[AnalystType.TRADER]
    ),
    AnalystConfiguration(
        name=AnalystType.SAFE_ANALYST,
        display_name="Conservative Analyst",
        description="Focuses on capital preservation and downside protection",
        team="Risk Management",
        color="#EF4444",
        icon="shield-check",
        dependencies=[AnalystType.TRADER]
    ),
    AnalystConfiguration(
        name=AnalystType.PORTFOLIO_MANAGER,
        display_name="Portfolio Manager",
        description="Makes final investment decisions and portfolio allocations",
        team="Portfolio Management",
        color="#F59E0B",
        icon="briefcase",
        dependencies=[AnalystType.RISKY_ANALYST, AnalystType.NEUTRAL_ANALYST, AnalystType.SAFE_ANALYST]
    )
]

DEFAULT_LLM_PROVIDERS = [
    LLMProviderConfig(
        name=LLMProvider.OPENAI,
        display_name="OpenAI",
        description="GPT models from OpenAI",
        models=[
            LLMModelInfo(
                name="gpt-4",
                display_name="GPT-4",
                description="Most capable model, best for complex reasoning",
                max_tokens=8192,
                recommended=True
            ),
            LLMModelInfo(
                name="gpt-4-turbo",
                display_name="GPT-4 Turbo",
                description="Faster and more cost-effective than GPT-4",
                max_tokens=128000,
                recommended=True
            ),
            LLMModelInfo(
                name="gpt-3.5-turbo",
                display_name="GPT-3.5 Turbo",
                description="Fast and cost-effective for simpler tasks",
                max_tokens=16385,
                recommended=False
            )
        ],
        api_key_required=True,
        enabled=True
    ),
    LLMProviderConfig(
        name=LLMProvider.ANTHROPIC,
        display_name="Anthropic",
        description="Claude models from Anthropic",
        models=[
            LLMModelInfo(
                name="claude-3-opus",
                display_name="Claude 3 Opus",
                description="Most powerful Claude model for complex tasks",
                max_tokens=200000,
                recommended=True
            ),
            LLMModelInfo(
                name="claude-3-sonnet",
                display_name="Claude 3 Sonnet",
                description="Balanced performance and speed",
                max_tokens=200000,
                recommended=True
            ),
            LLMModelInfo(
                name="claude-3-haiku",
                display_name="Claude 3 Haiku",
                description="Fastest Claude model for quick tasks",
                max_tokens=200000,
                recommended=False
            )
        ],
        api_key_required=True,
        enabled=True
    ),
    LLMProviderConfig(
        name=LLMProvider.GROQ,
        display_name="Groq",
        description="Ultra-fast inference with open-source models",
        models=[
            LLMModelInfo(
                name="llama2-70b-4096",
                display_name="Llama 2 70B",
                description="Large open-source model with good performance",
                max_tokens=4096,
                recommended=True
            ),
            LLMModelInfo(
                name="mixtral-8x7b-32768",
                display_name="Mixtral 8x7B",
                description="Mixture of experts model with large context",
                max_tokens=32768,
                recommended=True
            )
        ],
        api_key_required=True,
        enabled=True
    )
]
