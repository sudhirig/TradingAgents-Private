"""
Security middleware for TradingAgents Web Backend
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from ..utils.security import rate_limiter, get_client_id, SecurityHeaders

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Security middleware for rate limiting and security headers"""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        request = Request(scope, receive)
        
        # Skip security checks for health endpoints
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            await self.app(scope, receive, send)
            return
            
        # Rate limiting
        try:
            client_id = get_client_id(request)
            endpoint_type = self._get_endpoint_type(request.url.path)
            
            if not rate_limiter.is_allowed(client_id, endpoint_type):
                response = JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Please try again later."},
                    headers={"Retry-After": "60"}
                )
                await response(scope, receive, send)
                return
                
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Continue processing if rate limiting fails
            
        # Process request
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Add security headers
                headers = dict(message.get("headers", []))
                security_headers = SecurityHeaders.get_security_headers()
                
                for key, value in security_headers.items():
                    headers[key.encode()] = value.encode()
                    
                message["headers"] = list(headers.items())
                
            await send(message)
            
        await self.app(scope, receive, send_wrapper)
        
    def _get_endpoint_type(self, path: str) -> str:
        """Determine endpoint type for rate limiting"""
        if path.startswith("/api/analysis"):
            return "analysis"
        elif path.startswith("/ws"):
            return "websocket"
        elif path.startswith("/api/config"):
            return "config"
        elif path.startswith("/api/metrics"):
            return "metrics"
        else:
            return "default"

async def add_security_headers(request: Request, call_next: Callable) -> Response:
    """Add security headers to all responses"""
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Add security headers
        security_headers = SecurityHeaders.get_security_headers()
        for key, value in security_headers.items():
            response.headers[key] = value
            
        # Add processing time header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        logger.error(f"Security middleware error: {e}")
        # Return error response with security headers
        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
        
        security_headers = SecurityHeaders.get_security_headers()
        for key, value in security_headers.items():
            response.headers[key] = value
            
        return response

async def rate_limit_middleware(request: Request, call_next: Callable) -> Response:
    """Rate limiting middleware"""
    # Skip rate limiting for health endpoints
    if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
        return await call_next(request)
        
    try:
        client_id = get_client_id(request)
        endpoint_type = _get_endpoint_type(request.url.path)
        
        if not rate_limiter.is_allowed(client_id, endpoint_type):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."},
                headers={"Retry-After": "60"}
            )
            
        return await call_next(request)
        
    except Exception as e:
        logger.error(f"Rate limiting middleware error: {e}")
        return await call_next(request)

def _get_endpoint_type(path: str) -> str:
    """Determine endpoint type for rate limiting"""
    if path.startswith("/api/analysis"):
        return "analysis"
    elif path.startswith("/ws"):
        return "websocket"
    elif path.startswith("/api/config"):
        return "config"
    elif path.startswith("/api/metrics"):
        return "metrics"
    else:
        return "default"
