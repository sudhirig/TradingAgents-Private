#!/usr/bin/env python3
"""
Session Manager Service
Manages analysis sessions, state tracking, and session lifecycle
"""

import asyncio
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from enum import Enum

from ..models.analysis import (
    AnalysisRequest, AnalysisSession, AnalysisStatus, AgentStatus
)
logger = logging.getLogger(__name__)

class SessionState:
    """Individual session state management"""
    
    def __init__(self, session_id: str, request: AnalysisRequest):
        self.session_id = session_id
        self.request = request
        self.status = AnalysisStatus.PENDING
        self.progress = 0.0
        self.agent_statuses: Dict[str, AgentStatus] = {}
        self.reports: Dict[str, Optional[str]] = {}
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.last_activity = datetime.now()
        
        # Initialize agent statuses
        for analyst in request.selected_analysts:
            self.agent_statuses[analyst.value] = AgentStatus.PENDING
            
        # Initialize report sections
        self.reports = {
            "market_report": None,
            "sentiment_report": None,
            "news_report": None,
            "fundamentals_report": None,
            "investment_plan": None,
            "trader_investment_plan": None,
            "final_trade_decision": None
        }
        
    def update_agent_status(self, agent: str, status: AgentStatus, error_message: Optional[str] = None):
        """Update agent status"""
        self.agent_statuses[agent] = status
        self.last_activity = datetime.now()
        
        if status == AgentStatus.FAILED and error_message:
            self.error_message = f"Agent {agent} failed: {error_message}"
            
        # Update overall progress
        self._calculate_progress()
        
    def update_report_section(self, section: str, content: str):
        """Update report section"""
        self.reports[section] = content
        self.last_activity = datetime.now()
        
    def start_analysis(self):
        """Mark analysis as started"""
        self.status = AnalysisStatus.RUNNING
        self.started_at = datetime.now()
        self.last_activity = datetime.now()
        
    def complete_analysis(self, final_decision: Optional[str] = None):
        """Mark analysis as completed"""
        self.status = AnalysisStatus.COMPLETED
        self.completed_at = datetime.now()
        self.progress = 100.0
        self.last_activity = datetime.now()
        
        if final_decision:
            self.reports["final_trade_decision"] = final_decision
            
    def fail_analysis(self, error_message: str):
        """Mark analysis as failed"""
        self.status = AnalysisStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now()
        self.last_activity = datetime.now()
        
    def cancel_analysis(self):
        """Mark analysis as cancelled"""
        self.status = AnalysisStatus.CANCELLED
        self.completed_at = datetime.now()
        self.last_activity = datetime.now()
        
    def _calculate_progress(self):
        """Calculate overall progress based on agent statuses"""
        if not self.agent_statuses:
            self.progress = 0.0
            return
            
        total_agents = len(self.agent_statuses)
        completed_agents = sum(1 for status in self.agent_statuses.values() 
                             if status in [AgentStatus.COMPLETED, AgentStatus.FAILED])
        
        self.progress = (completed_agents / total_agents) * 100.0
        
        # Update overall status based on agent statuses
        if all(status == AgentStatus.COMPLETED for status in self.agent_statuses.values()):
            if self.status == AnalysisStatus.RUNNING:
                self.complete_analysis()
        elif any(status == AgentStatus.FAILED for status in self.agent_statuses.values()):
            if self.status == AnalysisStatus.RUNNING:
                failed_agents = [agent for agent, status in self.agent_statuses.items() 
                               if status == AgentStatus.FAILED]
                self.fail_analysis(f"Agents failed: {', '.join(failed_agents)}")
                
    def to_session_model(self) -> AnalysisSession:
        """Convert to AnalysisSession model"""
        return AnalysisSession(
            session_id=self.session_id,
            request=self.request,
            status=self.status,
            progress=self.progress,
            agent_statuses=self.agent_statuses,
            reports=self.reports,
            created_at=self.created_at,
            started_at=self.started_at,
            completed_at=self.completed_at,
            error_message=self.error_message
        )
        
    def is_expired(self, timeout_minutes: int = 60) -> bool:
        """Check if session is expired"""
        cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
        return self.last_activity < cutoff_time

class SessionManager:
    """Manages multiple analysis sessions"""
    
    def __init__(self, max_sessions: int = 100, session_timeout: int = 60):
        self.sessions: Dict[str, SessionState] = {}
        self.session_locks: Dict[str, asyncio.Lock] = {}
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        
        logger.info(f"Session Manager initialized (max_sessions={max_sessions}, timeout={session_timeout}min)")
        
    async def start(self):
        """Start background cleanup task"""
        if not self._running:
            self._running = True
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Session Manager started")
            
    async def stop(self):
        """Stop background tasks"""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Session Manager stopped")
        
    def create_session(self, request: AnalysisRequest) -> str:
        """Create a new analysis session"""
        # Check session limit
        if len(self.sessions) >= self.max_sessions:
            # Clean up expired sessions first
            self._cleanup_expired_sessions()
            
            # If still at limit, remove oldest session
            if len(self.sessions) >= self.max_sessions:
                oldest_session_id = min(self.sessions.keys(), 
                                      key=lambda sid: self.sessions[sid].created_at)
                self.remove_session(oldest_session_id)
                logger.warning(f"Removed oldest session {oldest_session_id} due to limit")
                
        session_id = str(uuid.uuid4())
        session_state = SessionState(session_id, request)
        
        self.sessions[session_id] = session_state
        self.session_locks[session_id] = asyncio.Lock()
        
        logger.info(f"Created session {session_id} for {request.ticker}")
        return session_id
        
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get session by ID"""
        return self.sessions.get(session_id)
        
    async def update_agent_status(self, session_id: str, agent: str, status: AgentStatus, 
                                error_message: Optional[str] = None) -> bool:
        """Update agent status in session"""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found for agent status update")
            return False
            
        async with self.session_locks[session_id]:
            session = self.sessions[session_id]
            session.update_agent_status(agent, status, error_message)
            
        logger.debug(f"Updated agent {agent} status to {status} in session {session_id}")
        return True
        
    async def update_report_section(self, session_id: str, section: str, content: str) -> bool:
        """Update report section in session"""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found for report update")
            return False
            
        async with self.session_locks[session_id]:
            session = self.sessions[session_id]
            session.update_report_section(section, content)
            
        logger.debug(f"Updated report section {section} in session {session_id}")
        return True
        
    async def start_analysis(self, session_id: str) -> bool:
        """Start analysis for session"""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found for analysis start")
            return False
            
        async with self.session_locks[session_id]:
            session = self.sessions[session_id]
            session.start_analysis()
            
        logger.info(f"Started analysis for session {session_id}")
        return True
        
    async def complete_analysis(self, session_id: str, final_decision: Optional[str] = None) -> bool:
        """Complete analysis for session"""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found for analysis completion")
            return False
            
        async with self.session_locks[session_id]:
            session = self.sessions[session_id]
            session.complete_analysis(final_decision)
            
        logger.info(f"Completed analysis for session {session_id}")
        return True
        
    async def fail_analysis(self, session_id: str, error_message: str) -> bool:
        """Fail analysis for session"""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found for analysis failure")
            return False
            
        async with self.session_locks[session_id]:
            session = self.sessions[session_id]
            session.fail_analysis(error_message)
            
        logger.error(f"Failed analysis for session {session_id}: {error_message}")
        return True
        
    async def cancel_analysis(self, session_id: str) -> bool:
        """Cancel analysis for session"""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found for analysis cancellation")
            return False
            
        async with self.session_locks[session_id]:
            session = self.sessions[session_id]
            session.cancel_analysis()
            
        logger.info(f"Cancelled analysis for session {session_id}")
        return True
        
    def remove_session(self, session_id: str) -> bool:
        """Remove session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if session_id in self.session_locks:
                del self.session_locks[session_id]
            logger.info(f"Removed session {session_id}")
            return True
        return False
        
    def get_all_sessions(self) -> List[AnalysisSession]:
        """Get all sessions as models"""
        return [session.to_session_model() for session in self.sessions.values()]
        
    def get_active_sessions(self) -> List[AnalysisSession]:
        """Get active (running) sessions"""
        return [session.to_session_model() for session in self.sessions.values()
                if session.status == AnalysisStatus.RUNNING]
        
    def get_session_count(self) -> int:
        """Get total number of sessions"""
        return len(self.sessions)
        
    def get_session_stats(self) -> Dict[str, int]:
        """Get session statistics"""
        stats = {
            "total": len(self.sessions),
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0
        }
        
        for session in self.sessions.values():
            stats[session.status.value] += 1
            
        return stats
        
    def _cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.is_expired(self.session_timeout)
        ]
        
        for session_id in expired_sessions:
            self.remove_session(session_id)
            
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
        return len(expired_sessions)
        
    async def _cleanup_loop(self):
        """Background cleanup task"""
        while self._running:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                self._cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")

# Global session manager instance
session_manager = SessionManager()

async def get_session_manager() -> SessionManager:
    """Get the global session manager instance"""
    if not session_manager._running:
        await session_manager.start()
    return session_manager
