"""
Performance metrics API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import psutil
import time
from ..utils.performance import performance_monitor
from ..utils.security import check_rate_limit

router = APIRouter()

@router.get("/performance")
async def get_performance_metrics() -> Dict[str, Any]:
    """Get current performance metrics"""
    try:
        # Get basic performance metrics
        metrics = performance_monitor.get_metrics()
        
        # Add system memory usage if available
        try:
            memory = psutil.virtual_memory()
            metrics['memoryUsage'] = {
                'used': memory.used,
                'total': memory.total,
                'percentage': memory.percent
            }
        except Exception:
            # psutil might not be available, skip memory metrics
            pass
            
        return {
            "websocketConnections": metrics['websocket_connections'],
            "activeSessions": metrics['active_sessions'],
            "messageRatePerSecond": metrics['message_rate_per_second'],
            "errorRatePerSecond": metrics['error_rate_per_second'],
            "averageResponseTimeMs": metrics['average_response_time_ms'],
            "totalMessagesInWindow": metrics['total_messages_in_window'],
            "totalErrorsInWindow": metrics['total_errors_in_window'],
            "memoryUsage": metrics.get('memoryUsage'),
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint with basic system info"""
    try:
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime": time.time() - performance_monitor.metrics.get('start_time', time.time()),
            "websocket_connections": performance_monitor.metrics['websocket_connections'],
            "active_sessions": performance_monitor.metrics['active_sessions']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
