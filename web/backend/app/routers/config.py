#!/usr/bin/env python3
"""
Configuration Router
API endpoints for application configuration, analyst info, and LLM providers
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
import logging

from app.models.config import (
    ConfigResponse, AnalystConfiguration, LLMProviderConfig,
    DEFAULT_ANALYST_CONFIGS, DEFAULT_LLM_PROVIDERS, DEFAULT_ANALYST_TEAMS
)
from app.models.analysis import AnalystType, LLMProvider

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/analysts", response_model=List[AnalystConfiguration])
async def get_analysts() -> List[AnalystConfiguration]:
    """Get available analysts configuration"""
    try:
        return DEFAULT_ANALYST_CONFIGS
    except Exception as e:
        logger.error(f"Error getting analysts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analysts")

@router.get("/llm-providers", response_model=List[LLMProviderConfig])
async def get_llm_providers() -> List[LLMProviderConfig]:
    """Get available LLM providers"""
    try:
        return DEFAULT_LLM_PROVIDERS
    except Exception as e:
        logger.error(f"Error getting LLM providers: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve LLM providers")

@router.get("/models/{provider}")
async def get_models_for_provider(provider: LLMProvider) -> Dict[str, Any]:
    """Get available models for a specific LLM provider"""
    try:
        for provider_config in DEFAULT_LLM_PROVIDERS:
            if provider_config.name == provider:
                return {
                    "provider": provider.value,
                    "models": [model.dict() for model in provider_config.models],
                    "enabled": provider_config.enabled
                }
        
        raise HTTPException(status_code=404, detail=f"Provider {provider} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting models for provider {provider}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve models")

@router.get("/teams")
async def get_analyst_teams() -> List[Dict[str, Any]]:
    """Get analyst team configurations"""
    try:
        return [team.dict() for team in DEFAULT_ANALYST_TEAMS]
    except Exception as e:
        logger.error(f"Error getting analyst teams: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analyst teams")

@router.get("/", response_model=ConfigResponse)
async def get_full_configuration() -> ConfigResponse:
    """Get complete application configuration"""
    try:
        # Convert analyst configs to AnalystInfo format for response
        analyst_infos = []
        for config in DEFAULT_ANALYST_CONFIGS:
            analyst_infos.append({
                "name": config.name,
                "description": config.description,
                "team": config.team,
                "color": config.color
            })
        
        # Extract LLM providers
        llm_providers = [provider.name for provider in DEFAULT_LLM_PROVIDERS]
        
        # Build models dict
        models_dict = {}
        for provider_config in DEFAULT_LLM_PROVIDERS:
            models_dict[provider_config.name.value] = [
                model.name for model in provider_config.models
            ]
        
        return ConfigResponse(
            analysts=analyst_infos,
            llm_providers=llm_providers,
            models=models_dict,
            max_research_depth=5,
            default_config={
                "temperature": 0.7,
                "max_tokens": None,
                "research_depth": 1,
                "selected_analysts": ["Market Analyst", "Social Analyst"],
                "llm_provider": "openai",
                "llm_model": "gpt-4"
            }
        )
    except Exception as e:
        logger.error(f"Error getting full configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve configuration")

@router.get("/defaults")
async def get_default_configuration() -> Dict[str, Any]:
    """Get default configuration values"""
    try:
        return {
            "ticker": "TSLA",
            "trade_date": "2025-01-15",
            "selected_analysts": [
                AnalystType.MARKET_ANALYST.value,
                AnalystType.SOCIAL_ANALYST.value,
                AnalystType.FUNDAMENTALS_ANALYST.value
            ],
            "research_depth": 1,
            "llm_config": {
                "provider": LLMProvider.OPENAI.value,
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": None
            }
        }
    except Exception as e:
        logger.error(f"Error getting default configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve default configuration")

@router.get("/validation-rules")
async def get_validation_rules() -> Dict[str, Any]:
    """Get validation rules for configuration"""
    try:
        return {
            "ticker": {
                "min_length": 1,
                "max_length": 10,
                "pattern": "^[A-Z]+$",
                "description": "Stock ticker symbol (uppercase letters only)"
            },
            "trade_date": {
                "format": "YYYY-MM-DD",
                "description": "Trade date in ISO format"
            },
            "selected_analysts": {
                "min_items": 1,
                "max_items": len(AnalystType),
                "available_options": [analyst.value for analyst in AnalystType],
                "description": "List of analysts to include in analysis"
            },
            "research_depth": {
                "minimum": 1,
                "maximum": 5,
                "description": "Research depth level (1=basic, 5=comprehensive)"
            },
            "llm_config": {
                "temperature": {
                    "minimum": 0.0,
                    "maximum": 2.0,
                    "description": "LLM temperature for response generation"
                },
                "max_tokens": {
                    "minimum": 1,
                    "maximum": 200000,
                    "description": "Maximum tokens to generate (optional)"
                }
            }
        }
    except Exception as e:
        logger.error(f"Error getting validation rules: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve validation rules")
