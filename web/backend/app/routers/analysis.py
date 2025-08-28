#!/usr/bin/env python3
"""
Analysis Router
API endpoints for analysis session management and execution
"""

import uuid
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from ..models.analysis import (
    AnalysisRequest, AnalysisResponse, AnalysisSession, 
    AnalysisStatus, AgentStatus, AnalysisReports, AnalysisSessionStatus
)
from ..services.analysis_service import get_analysis_service
from ..utils.security import check_rate_limit, input_validator
from ..utils.performance import performance_monitor, performance_timer
from ..services.session_manager import SessionManager

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/start", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks) -> AnalysisResponse:
    """Start a new analysis session"""
    try:
        # Get session manager
        session_manager = await get_session_manager()
        
        # Create new session
        session_id = session_manager.create_session(request)
        
        # Get analysis service
        analysis_service = get_analysis_service()
        
        # Start analysis in background
        success = await analysis_service.start_analysis(session_id, request)
        
        if not success:
            raise HTTPException(
                status_code=503, 
                detail="Maximum concurrent analyses reached. Please try again later."
            )
        
        logger.info(f"Started analysis session {session_id} for {request.ticker}")
        
        return AnalysisResponse(
            session_id=session_id,
            status=AnalysisStatus.PENDING,
            message=f"Analysis started for {request.ticker}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to start analysis")

@router.get("/{session_id}/status", response_model=AnalysisSession)
async def get_analysis_status(session_id: str) -> AnalysisSession:
    """Get current status of an analysis session"""
    try:
        session_manager = await get_session_manager()
        session = session_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Calculate current agent
        current_agent = None
        for agent, status in session.agent_statuses.items():
            if status.value == "in_progress":
                current_agent = agent
                break
        
        return AnalysisSessionStatus(
            session_id=session_id,
            status=session.status,
            progress=session.progress,
            agent_statuses=session.agent_statuses,
            current_agent=current_agent,
            created_at=session.created_at,
            started_at=session.started_at,
            completed_at=session.completed_at,
            error_message=session.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis status for {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analysis status")

@router.get("/{session_id}/reports", response_model=AnalysisReports)
async def get_analysis_reports(session_id: str) -> AnalysisReports:
    """Get current reports for an analysis session"""
    try:
        session_manager = await get_session_manager()
        session = session_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return AnalysisReports(
            session_id=session_id,
            reports=session.reports,
            final_trade_decision=session.reports.get("final_trade_decision"),
            last_updated=session.last_activity
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis reports for {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analysis reports")

@router.post("/{session_id}/cancel")
async def cancel_analysis(session_id: str) -> Dict[str, str]:
    """Cancel a running analysis session"""
    try:
        session_manager = await get_session_manager()
        session = session_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.status not in [AnalysisStatus.PENDING, AnalysisStatus.RUNNING]:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot cancel analysis in status: {session.status}"
            )
        
        # Cancel analysis
        analysis_service = get_analysis_service()
        await analysis_service.cancel_analysis(session_id)
        
        # Update session status
        await session_manager.cancel_analysis(session_id)
        
        logger.info(f"Cancelled analysis session {session_id}")
        
        return {"message": f"Analysis {session_id} cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling analysis {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel analysis")

@router.delete("/{session_id}")
async def delete_analysis_session(session_id: str) -> Dict[str, str]:
    """Delete an analysis session"""
    try:
        session_manager = await get_session_manager()
        session = session_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Cancel if running
        if session.status in [AnalysisStatus.PENDING, AnalysisStatus.RUNNING]:
            analysis_service = get_analysis_service()
            await analysis_service.cancel_analysis(session_id)
        
        # Remove session
        session_manager.remove_session(session_id)
        
        logger.info(f"Deleted analysis session {session_id}")
        
        return {"message": f"Session {session_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analysis session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")

@router.get("/", response_model=List[AnalysisSessionStatus])
async def list_analysis_sessions() -> List[AnalysisSessionStatus]:
    """List all analysis sessions"""
    try:
        session_manager = await get_session_manager()
        sessions = session_manager.get_all_sessions()
        
        # Convert to status responses
        session_statuses = []
        for session_model in sessions:
            # Calculate current agent
            current_agent = None
            for agent, status in session_model.agent_statuses.items():
                if status.value == "in_progress":
                    current_agent = agent
                    break
            
            session_statuses.append(AnalysisSessionStatus(
                session_id=session_model.session_id,
                status=session_model.status,
                progress=session_model.progress,
                agent_statuses=session_model.agent_statuses,
                current_agent=current_agent,
                created_at=session_model.created_at,
                started_at=session_model.started_at,
                completed_at=session_model.completed_at,
                error_message=session_model.error_message
            ))
        
        return session_statuses
        
    except Exception as e:
        logger.error(f"Error listing analysis sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list sessions")

@router.get("/stats")
async def get_analysis_stats() -> Dict[str, Any]:
    """Get analysis statistics"""
    try:
        session_manager = await get_session_manager()
        stats = session_manager.get_session_stats()
        
        return {
            "session_stats": stats,
            "active_sessions": stats.get("running", 0),
            "total_sessions": stats.get("total", 0),
            "success_rate": (
                stats.get("completed", 0) / max(stats.get("total", 1), 1) * 100
                if stats.get("total", 0) > 0 else 0
            )
        }
        
    except Exception as e:
        logger.error(f"Error getting analysis stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

@router.post("/{session_id}/retry")
async def retry_analysis(session_id: str) -> AnalysisResponse:
    """Retry a failed analysis session"""
    try:
        session_manager = await get_session_manager()
        session = session_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.status != AnalysisStatus.FAILED:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot retry analysis in status: {session.status}"
            )
        
        # Reset session state
        session.status = AnalysisStatus.PENDING
        session.progress = 0.0
        session.error_message = None
        session.started_at = None
        session.completed_at = None
        
        # Reset agent statuses
        for agent in session.agent_statuses:
            session.agent_statuses[agent] = "pending"
        
        # Start analysis again
        analysis_service = get_analysis_service()
        success = await analysis_service.start_analysis(session_id, session.request)
        
        if not success:
            raise HTTPException(
                status_code=503,
                detail="Maximum concurrent analyses reached. Please try again later."
            )
        
        logger.info(f"Retrying analysis session {session_id}")
        
        return AnalysisResponse(
            session_id=session_id,
            status=AnalysisStatus.PENDING,
            message=f"Analysis retry started for session {session_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying analysis {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retry analysis")
