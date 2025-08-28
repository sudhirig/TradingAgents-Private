#!/usr/bin/env python3
"""
WebSocket Message Models
Pydantic models for real-time WebSocket communication
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field
from .analysis import AnalystType, AgentStatus

class WebSocketMessageType(str):
    """WebSocket message types"""
    AGENT_STATUS_UPDATE = "agent_status_update"
    MESSAGE_UPDATE = "message_update"
    TOOL_CALL = "tool_call"
    REPORT_UPDATE = "report_update"
    ANALYSIS_COMPLETE = "analysis_complete"
    ANALYSIS_ERROR = "analysis_error"
    CONNECTION_ACK = "connection_ack"
    HEARTBEAT = "heartbeat"

class BaseWebSocketMessage(BaseModel):
    """Base WebSocket message"""
    type: str = Field(..., description="Message type")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    session_id: str = Field(..., description="Session identifier")

class AgentStatusUpdateMessage(BaseWebSocketMessage):
    """Agent status update message"""
    type: Literal["agent_status_update"] = "agent_status_update"
    agent: str = Field(..., description="Agent name")
    status: AgentStatus = Field(..., description="Agent status")
    start_time: Optional[datetime] = Field(None, description="Agent start time")
    end_time: Optional[datetime] = Field(None, description="Agent completion time")
    progress: Optional[float] = Field(None, ge=0.0, le=100.0, description="Agent progress percentage")

class MessageUpdateMessage(BaseWebSocketMessage):
    """Message/reasoning update"""
    type: Literal["message_update"] = "message_update"
    message_type: str = Field(..., description="Type of message (Reasoning, Tool Call, etc.)")
    content: str = Field(..., description="Message content")
    agent: Optional[str] = Field(None, description="Agent that generated the message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata")

class ToolCallMessage(BaseWebSocketMessage):
    """Tool call message"""
    type: Literal["tool_call"] = "tool_call"
    tool_name: str = Field(..., description="Name of the tool being called")
    args: Dict[str, Any] = Field(..., description="Tool arguments")
    agent: Optional[str] = Field(None, description="Agent making the tool call")
    call_id: Optional[str] = Field(None, description="Unique call identifier")

class ToolResultMessage(BaseWebSocketMessage):
    """Tool result message"""
    type: Literal["tool_result"] = "tool_result"
    tool_name: str = Field(..., description="Name of the tool")
    call_id: Optional[str] = Field(None, description="Call identifier")
    result: Any = Field(..., description="Tool execution result")
    success: bool = Field(..., description="Whether tool call was successful")
    error: Optional[str] = Field(None, description="Error message if failed")

class ReportUpdateMessage(BaseWebSocketMessage):
    """Report section update message"""
    type: Literal["report_update"] = "report_update"
    section: str = Field(..., description="Report section name")
    content: str = Field(..., description="Report content in markdown")
    agent: Optional[str] = Field(None, description="Agent that generated the report")
    is_final: bool = Field(False, description="Whether this is the final version")

class AnalysisCompleteMessage(BaseWebSocketMessage):
    """Analysis completion message"""
    type: Literal["analysis_complete"] = "analysis_complete"
    final_trade_decision: Optional[str] = Field(None, description="Final trading decision")
    summary: Optional[str] = Field(None, description="Analysis summary")
    duration: Optional[float] = Field(None, description="Total analysis duration in seconds")
    total_agents: int = Field(..., description="Total number of agents involved")
    successful_agents: int = Field(..., description="Number of successfully completed agents")

class AnalysisErrorMessage(BaseWebSocketMessage):
    """Analysis error message"""
    type: Literal["analysis_error"] = "analysis_error"
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error description")
    agent: Optional[str] = Field(None, description="Agent where error occurred")
    recoverable: bool = Field(False, description="Whether error is recoverable")

class ConnectionAckMessage(BaseWebSocketMessage):
    """Connection acknowledgment message"""
    type: Literal["connection_ack"] = "connection_ack"
    message: str = Field("WebSocket connection established", description="Acknowledgment message")
    server_time: datetime = Field(default_factory=datetime.now, description="Server timestamp")

class HeartbeatMessage(BaseWebSocketMessage):
    """Heartbeat/ping message"""
    type: Literal["heartbeat"] = "heartbeat"
    server_time: datetime = Field(default_factory=datetime.now, description="Server timestamp")

class ProgressUpdateMessage(BaseWebSocketMessage):
    """Overall progress update message"""
    type: Literal["progress_update"] = "progress_update"
    overall_progress: float = Field(..., ge=0.0, le=100.0, description="Overall analysis progress")
    current_phase: str = Field(..., description="Current analysis phase")
    agents_completed: int = Field(..., description="Number of completed agents")
    agents_total: int = Field(..., description="Total number of agents")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")

# Union type for all WebSocket messages
WebSocketMessage = Union[
    AgentStatusUpdateMessage,
    MessageUpdateMessage,
    ToolCallMessage,
    ToolResultMessage,
    ReportUpdateMessage,
    AnalysisCompleteMessage,
    AnalysisErrorMessage,
    ConnectionAckMessage,
    HeartbeatMessage,
    ProgressUpdateMessage
]

class WebSocketResponse(BaseModel):
    """WebSocket response wrapper"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

class WebSocketError(BaseModel):
    """WebSocket error response"""
    type: Literal["error"] = "error"
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    session_id: Optional[str] = Field(None, description="Session identifier")

# Message factory functions
def create_agent_status_message(
    session_id: str,
    agent: str,
    status: AgentStatus,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    progress: Optional[float] = None
) -> AgentStatusUpdateMessage:
    """Create agent status update message"""
    return AgentStatusUpdateMessage(
        session_id=session_id,
        agent=agent,
        status=status,
        start_time=start_time,
        end_time=end_time,
        progress=progress
    )

def create_message_update(
    session_id: str,
    message_type: str,
    content: str,
    agent: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> MessageUpdateMessage:
    """Create message update"""
    return MessageUpdateMessage(
        session_id=session_id,
        message_type=message_type,
        content=content,
        agent=agent,
        metadata=metadata
    )

def create_tool_call_message(
    session_id: str,
    tool_name: str,
    args: Dict[str, Any],
    agent: Optional[str] = None,
    call_id: Optional[str] = None
) -> ToolCallMessage:
    """Create tool call message"""
    return ToolCallMessage(
        session_id=session_id,
        tool_name=tool_name,
        args=args,
        agent=agent,
        call_id=call_id
    )

def create_report_update_message(
    session_id: str,
    section: str,
    content: str,
    agent: Optional[str] = None,
    is_final: bool = False
) -> ReportUpdateMessage:
    """Create report update message"""
    return ReportUpdateMessage(
        session_id=session_id,
        section=section,
        content=content,
        agent=agent,
        is_final=is_final
    )

def create_analysis_complete_message(
    session_id: str,
    final_trade_decision: Optional[str] = None,
    summary: Optional[str] = None,
    duration: Optional[float] = None,
    total_agents: int = 0,
    successful_agents: int = 0
) -> AnalysisCompleteMessage:
    """Create analysis complete message"""
    return AnalysisCompleteMessage(
        session_id=session_id,
        final_trade_decision=final_trade_decision,
        summary=summary,
        duration=duration,
        total_agents=total_agents,
        successful_agents=successful_agents
    )

def create_error_message(
    session_id: str,
    error_type: str,
    error_message: str,
    agent: Optional[str] = None,
    recoverable: bool = False
) -> AnalysisErrorMessage:
    """Create error message"""
    return AnalysisErrorMessage(
        session_id=session_id,
        error_type=error_type,
        error_message=error_message,
        agent=agent,
        recoverable=recoverable
    )

class WebSocketStats(BaseModel):
    """WebSocket connection statistics"""
    total_connections: int = Field(default=0, description="Total connections")
    active_connections: int = Field(default=0, description="Active connections")
    messages_sent: int = Field(default=0, description="Messages sent")
    messages_received: int = Field(default=0, description="Messages received")
    uptime_seconds: float = Field(default=0.0, description="Uptime in seconds")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")

