"""
Performance optimization utilities for TradingAgents Web Backend
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional
from collections import deque
from dataclasses import dataclass
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

@dataclass
class MessageBatch:
    """Batch of WebSocket messages for efficient transmission"""
    session_id: str
    messages: List[Dict[str, Any]]
    created_at: float
    
class MessageBatcher:
    """Batches WebSocket messages to reduce transmission overhead"""
    
    def __init__(self, batch_size: int = 10, batch_timeout: float = 0.5):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.pending_batches: Dict[str, MessageBatch] = {}
        self.batch_tasks: Dict[str, asyncio.Task] = {}
        
    async def add_message(self, session_id: str, message: Dict[str, Any], 
                         send_callback) -> None:
        """Add message to batch for session"""
        current_time = time.time()
        
        # Create new batch if none exists
        if session_id not in self.pending_batches:
            self.pending_batches[session_id] = MessageBatch(
                session_id=session_id,
                messages=[],
                created_at=current_time
            )
            
        batch = self.pending_batches[session_id]
        batch.messages.append(message)
        
        # Send immediately if batch is full
        if len(batch.messages) >= self.batch_size:
            await self._send_batch(session_id, send_callback)
        else:
            # Schedule timeout-based send if not already scheduled
            if session_id not in self.batch_tasks:
                self.batch_tasks[session_id] = asyncio.create_task(
                    self._schedule_batch_send(session_id, send_callback)
                )
                
    async def _schedule_batch_send(self, session_id: str, send_callback) -> None:
        """Schedule batch send after timeout"""
        try:
            await asyncio.sleep(self.batch_timeout)
            if session_id in self.pending_batches:
                await self._send_batch(session_id, send_callback)
        except asyncio.CancelledError:
            pass
        finally:
            self.batch_tasks.pop(session_id, None)
            
    async def _send_batch(self, session_id: str, send_callback) -> None:
        """Send batched messages"""
        if session_id not in self.pending_batches:
            return
            
        batch = self.pending_batches.pop(session_id)
        
        # Cancel scheduled send task
        if session_id in self.batch_tasks:
            self.batch_tasks[session_id].cancel()
            self.batch_tasks.pop(session_id, None)
            
        if batch.messages:
            try:
                # Send as batch or individual messages based on count
                if len(batch.messages) == 1:
                    await send_callback(batch.messages[0])
                else:
                    batch_message = {
                        "type": "message_batch",
                        "session_id": session_id,
                        "timestamp": time.time(),
                        "data": {
                            "messages": batch.messages,
                            "count": len(batch.messages)
                        }
                    }
                    await send_callback(batch_message)
                    
                logger.debug(f"Sent batch of {len(batch.messages)} messages for session {session_id}")
                
            except Exception as e:
                logger.error(f"Failed to send message batch for session {session_id}: {e}")

class MemoryManager:
    """Manages memory usage and cleanup for WebSocket connections"""
    
    def __init__(self, max_messages_per_session: int = 1000, 
                 max_sessions: int = 100):
        self.max_messages_per_session = max_messages_per_session
        self.max_sessions = max_sessions
        self.session_messages: Dict[str, deque] = {}
        self.session_last_activity: Dict[str, float] = {}
        
    def add_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """Add message to session history with memory management"""
        current_time = time.time()
        
        # Initialize session if new
        if session_id not in self.session_messages:
            self.session_messages[session_id] = deque(maxlen=self.max_messages_per_session)
            
        # Add message and update activity
        self.session_messages[session_id].append(message)
        self.session_last_activity[session_id] = current_time
        
        # Clean up old sessions if needed
        if len(self.session_messages) > self.max_sessions:
            self._cleanup_old_sessions()
            
    def get_session_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get messages for session with optional limit"""
        if session_id not in self.session_messages:
            return []
            
        messages = list(self.session_messages[session_id])
        if limit:
            return messages[-limit:]
        return messages
        
    def cleanup_session(self, session_id: str) -> None:
        """Clean up session data"""
        self.session_messages.pop(session_id, None)
        self.session_last_activity.pop(session_id, None)
        logger.debug(f"Cleaned up session {session_id}")
        
    def _cleanup_old_sessions(self) -> None:
        """Clean up least recently used sessions"""
        if not self.session_last_activity:
            return
            
        # Sort sessions by last activity
        sorted_sessions = sorted(
            self.session_last_activity.items(),
            key=lambda x: x[1]
        )
        
        # Remove oldest sessions until under limit
        sessions_to_remove = len(sorted_sessions) - self.max_sessions + 1
        for session_id, _ in sorted_sessions[:sessions_to_remove]:
            self.cleanup_session(session_id)
            
        logger.info(f"Cleaned up {sessions_to_remove} old sessions")

class PerformanceMonitor:
    """Monitors performance metrics for the application"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metrics = {
            'websocket_connections': 0,
            'active_sessions': 0,
            'messages_sent': deque(maxlen=window_size),
            'response_times': deque(maxlen=window_size),
            'error_count': deque(maxlen=window_size),
        }
        
    def record_websocket_connection(self, connected: bool) -> None:
        """Record WebSocket connection change"""
        if connected:
            self.metrics['websocket_connections'] += 1
        else:
            self.metrics['websocket_connections'] = max(0, self.metrics['websocket_connections'] - 1)
            
    def record_session_change(self, active: bool) -> None:
        """Record session change"""
        if active:
            self.metrics['active_sessions'] += 1
        else:
            self.metrics['active_sessions'] = max(0, self.metrics['active_sessions'] - 1)
            
    def record_message_sent(self, timestamp: Optional[float] = None) -> None:
        """Record message sent"""
        self.metrics['messages_sent'].append(timestamp or time.time())
        
    def record_response_time(self, response_time: float) -> None:
        """Record API response time"""
        self.metrics['response_times'].append(response_time)
        
    def record_error(self, timestamp: Optional[float] = None) -> None:
        """Record error occurrence"""
        self.metrics['error_count'].append(timestamp or time.time())
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        current_time = time.time()
        
        # Calculate rates (per second)
        message_rate = self._calculate_rate(self.metrics['messages_sent'], current_time)
        error_rate = self._calculate_rate(self.metrics['error_count'], current_time)
        
        # Calculate average response time
        avg_response_time = (
            sum(self.metrics['response_times']) / len(self.metrics['response_times'])
            if self.metrics['response_times'] else 0
        )
        
        return {
            'websocket_connections': self.metrics['websocket_connections'],
            'active_sessions': self.metrics['active_sessions'],
            'message_rate_per_second': message_rate,
            'error_rate_per_second': error_rate,
            'average_response_time_ms': avg_response_time * 1000,
            'total_messages_in_window': len(self.metrics['messages_sent']),
            'total_errors_in_window': len(self.metrics['error_count']),
        }
        
    def _calculate_rate(self, timestamps: deque, current_time: float) -> float:
        """Calculate rate per second from timestamps"""
        if not timestamps:
            return 0.0
            
        # Count events in last second
        recent_events = sum(1 for ts in timestamps if current_time - ts <= 1.0)
        return float(recent_events)

@asynccontextmanager
async def performance_timer():
    """Context manager for timing operations"""
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        duration = end_time - start_time
        logger.debug(f"Operation completed in {duration:.3f}s")

# Global instances
message_batcher = MessageBatcher()
memory_manager = MemoryManager()
performance_monitor = PerformanceMonitor()
