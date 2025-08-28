"""
Security utilities for TradingAgents Web Backend
"""

import time
import hashlib
import secrets
import logging
from typing import Dict, Set, Optional, Any
from collections import defaultdict, deque
from dataclasses import dataclass
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import re

logger = logging.getLogger(__name__)

@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""
    requests_per_window: int
    window_seconds: int
    burst_allowance: int = 0

class RateLimiter:
    """Token bucket rate limiter with burst support"""
    
    def __init__(self):
        self.client_buckets: Dict[str, Dict[str, Any]] = {}
        self.rules: Dict[str, RateLimitRule] = {
            'analysis': RateLimitRule(requests_per_window=5, window_seconds=60, burst_allowance=2),
            'websocket': RateLimitRule(requests_per_window=100, window_seconds=60, burst_allowance=10),
            'config': RateLimitRule(requests_per_window=20, window_seconds=60, burst_allowance=5),
            'default': RateLimitRule(requests_per_window=30, window_seconds=60, burst_allowance=5)
        }
        
    def is_allowed(self, client_id: str, endpoint_type: str = 'default') -> bool:
        """Check if request is allowed under rate limit"""
        rule = self.rules.get(endpoint_type, self.rules['default'])
        current_time = time.time()
        
        # Initialize client bucket if new
        if client_id not in self.client_buckets:
            self.client_buckets[client_id] = {
                'tokens': rule.requests_per_window + rule.burst_allowance,
                'last_refill': current_time,
                'requests': deque(maxlen=rule.requests_per_window * 2)
            }
            
        bucket = self.client_buckets[client_id]
        
        # Refill tokens based on time elapsed
        time_elapsed = current_time - bucket['last_refill']
        tokens_to_add = (time_elapsed / rule.window_seconds) * rule.requests_per_window
        bucket['tokens'] = min(
            rule.requests_per_window + rule.burst_allowance,
            bucket['tokens'] + tokens_to_add
        )
        bucket['last_refill'] = current_time
        
        # Check if request is allowed
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            bucket['requests'].append(current_time)
            return True
            
        logger.warning(f"Rate limit exceeded for client {client_id} on {endpoint_type}")
        return False
        
    def get_client_stats(self, client_id: str) -> Dict[str, Any]:
        """Get rate limiting stats for client"""
        if client_id not in self.client_buckets:
            return {'tokens': 0, 'requests_in_window': 0}
            
        bucket = self.client_buckets[client_id]
        current_time = time.time()
        
        # Count recent requests
        recent_requests = sum(
            1 for req_time in bucket['requests'] 
            if current_time - req_time <= 60
        )
        
        return {
            'tokens': int(bucket['tokens']),
            'requests_in_window': recent_requests,
            'last_request': bucket['last_refill']
        }

class InputValidator:
    """Validates and sanitizes user inputs"""
    
    # Regex patterns for validation
    PATTERNS = {
        'ticker': re.compile(r'^[A-Z]{1,5}$'),
        'session_id': re.compile(r'^[a-zA-Z0-9_-]{8,64}$'),
        'analyst_name': re.compile(r'^[a-zA-Z\s]{3,50}$'),
        'llm_provider': re.compile(r'^(openai|anthropic|groq)$'),
        'model_name': re.compile(r'^[a-zA-Z0-9._-]{3,50}$'),
        'date': re.compile(r'^\d{4}-\d{2}-\d{2}$')
    }
    
    # Maximum lengths for string fields
    MAX_LENGTHS = {
        'ticker': 5,
        'session_id': 64,
        'analyst_name': 50,
        'llm_provider': 20,
        'model_name': 50,
        'message_content': 10000,
        'report_content': 100000
    }
    
    @classmethod
    def validate_ticker(cls, ticker: str) -> str:
        """Validate stock ticker symbol"""
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
            
        ticker = ticker.upper().strip()
        if not cls.PATTERNS['ticker'].match(ticker):
            raise ValueError("Ticker must be 1-5 uppercase letters")
            
        return ticker
        
    @classmethod
    def validate_session_id(cls, session_id: str) -> str:
        """Validate session ID format"""
        if not session_id or not isinstance(session_id, str):
            raise ValueError("Session ID must be a non-empty string")
            
        session_id = session_id.strip()
        if not cls.PATTERNS['session_id'].match(session_id):
            raise ValueError("Session ID must be 8-64 alphanumeric characters, hyphens, or underscores")
            
        return session_id
        
    @classmethod
    def validate_analyst_list(cls, analysts: list) -> list:
        """Validate list of analyst names"""
        if not isinstance(analysts, list):
            raise ValueError("Analysts must be a list")
            
        if not analysts:
            raise ValueError("At least one analyst must be selected")
            
        if len(analysts) > 20:
            raise ValueError("Too many analysts selected (max 20)")
            
        validated_analysts = []
        for analyst in analysts:
            if not isinstance(analyst, str):
                raise ValueError("Analyst names must be strings")
                
            analyst = analyst.strip()
            if not cls.PATTERNS['analyst_name'].match(analyst):
                raise ValueError(f"Invalid analyst name: {analyst}")
                
            validated_analysts.append(analyst)
            
        return validated_analysts
        
    @classmethod
    def validate_llm_config(cls, config: dict) -> dict:
        """Validate LLM configuration"""
        if not isinstance(config, dict):
            raise ValueError("LLM config must be a dictionary")
            
        required_fields = ['provider', 'model']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
                
        # Validate provider
        provider = config['provider'].lower().strip()
        if not cls.PATTERNS['llm_provider'].match(provider):
            raise ValueError("Invalid LLM provider")
            
        # Validate model
        model = config['model'].strip()
        if not cls.PATTERNS['model_name'].match(model):
            raise ValueError("Invalid model name")
            
        # Validate optional parameters
        validated_config = {
            'provider': provider,
            'model': model
        }
        
        if 'temperature' in config:
            temp = float(config['temperature'])
            if not 0 <= temp <= 2:
                raise ValueError("Temperature must be between 0 and 2")
            validated_config['temperature'] = temp
            
        if 'max_tokens' in config:
            max_tokens = int(config['max_tokens'])
            if not 1 <= max_tokens <= 32000:
                raise ValueError("Max tokens must be between 1 and 32000")
            validated_config['max_tokens'] = max_tokens
            
        return validated_config
        
    @classmethod
    def sanitize_content(cls, content: str, max_length: int = 10000) -> str:
        """Sanitize text content"""
        if not isinstance(content, str):
            return ""
            
        # Remove null bytes and control characters
        content = ''.join(char for char in content if ord(char) >= 32 or char in '\n\r\t')
        
        # Truncate if too long
        if len(content) > max_length:
            content = content[:max_length] + "..."
            
        return content.strip()

class SecurityHeaders:
    """Security headers middleware"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get recommended security headers"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }

class SessionManager:
    """Secure session management"""
    
    def __init__(self, session_timeout: int = 3600):
        self.session_timeout = session_timeout
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
    def create_session(self, client_id: str) -> str:
        """Create new secure session"""
        session_id = self._generate_session_id()
        current_time = time.time()
        
        self.active_sessions[session_id] = {
            'client_id': client_id,
            'created_at': current_time,
            'last_activity': current_time,
            'is_active': True
        }
        
        logger.info(f"Created session {session_id} for client {client_id}")
        return session_id
        
    def validate_session(self, session_id: str) -> bool:
        """Validate session and update activity"""
        if session_id not in self.active_sessions:
            return False
            
        session = self.active_sessions[session_id]
        current_time = time.time()
        
        # Check if session expired
        if current_time - session['last_activity'] > self.session_timeout:
            self.invalidate_session(session_id)
            return False
            
        # Update last activity
        session['last_activity'] = current_time
        return session['is_active']
        
    def invalidate_session(self, session_id: str) -> None:
        """Invalidate session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['is_active'] = False
            logger.info(f"Invalidated session {session_id}")
            
    def cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if current_time - session['last_activity'] > self.session_timeout:
                expired_sessions.append(session_id)
                
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            logger.debug(f"Cleaned up expired session {session_id}")
            
    def _generate_session_id(self) -> str:
        """Generate cryptographically secure session ID"""
        return secrets.token_urlsafe(32)
        
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        current_time = time.time()
        active_count = sum(
            1 for session in self.active_sessions.values()
            if session['is_active'] and current_time - session['last_activity'] <= self.session_timeout
        )
        
        return {
            'total_sessions': len(self.active_sessions),
            'active_sessions': active_count,
            'expired_sessions': len(self.active_sessions) - active_count
        }

# Global instances
rate_limiter = RateLimiter()
input_validator = InputValidator()
session_manager = SessionManager()

def get_client_id(request: Request) -> str:
    """Extract client identifier from request"""
    # Use X-Forwarded-For if behind proxy, otherwise use client IP
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        client_ip = forwarded_for.split(',')[0].strip()
    else:
        client_ip = request.client.host if request.client else 'unknown'
        
    # Create hash of IP + User-Agent for better client identification
    user_agent = request.headers.get('User-Agent', '')
    client_string = f"{client_ip}:{user_agent}"
    
    return hashlib.sha256(client_string.encode()).hexdigest()[:16]

async def check_rate_limit(request: Request, endpoint_type: str = 'default') -> None:
    """Middleware to check rate limits"""
    client_id = get_client_id(request)
    
    if not rate_limiter.is_allowed(client_id, endpoint_type):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "60"}
        )
