#!/usr/bin/env python3
"""
Analysis Service
Thread-safe wrapper around TradingAgentsGraph for web backend integration
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, AsyncGenerator
import threading
from concurrent.futures import ThreadPoolExecutor
import queue

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
sys.path.insert(0, project_root)

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from ..models.analysis import AnalysisRequest, AnalysisStatus, AgentStatus
from ..models.websocket import (
    AgentStatusUpdateMessage, MessageUpdateMessage, ToolCallMessage, ReportUpdateMessage, 
    AnalysisCompleteMessage, AnalysisErrorMessage,
    create_agent_status_message, create_message_update, create_report_update_message, 
    create_analysis_complete_message, create_error_message
)
from .websocket_manager import get_websocket_manager
from .session_manager import get_session_manager

logger = logging.getLogger(__name__)

class AnalysisStreamHandler:
    """Handles streaming analysis results and WebSocket broadcasting"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.websocket_manager = None
        self.session_manager = None
        self.current_agent = None
        self.agent_start_times: Dict[str, datetime] = {}
        
    async def initialize(self):
        """Initialize managers"""
        self.websocket_manager = await get_websocket_manager()
        self.session_manager = await get_session_manager()
        
    async def handle_chunk(self, chunk: Dict[str, Any]):
        """Process a single chunk from the analysis stream"""
        try:
            # Extract messages
            if "messages" in chunk and len(chunk["messages"]) > 0:
                await self._handle_messages(chunk["messages"])
                
            # Handle agent status updates
            await self._handle_agent_status(chunk)
            
            # Handle report updates
            await self._handle_reports(chunk)
            
        except Exception as e:
            logger.error(f"Error handling chunk in session {self.session_id}: {e}")
            await self._broadcast_error("chunk_processing_error", str(e))
            
    async def _handle_messages(self, messages: list):
        """Handle message updates from chunk"""
        for message in messages:
            try:
                content = self._extract_content_string(message.content)
                message_type = getattr(message, 'type', 'Unknown')
                
                # Determine agent from message context
                agent = self._determine_agent_from_message(message)
                
                # Create and broadcast message update
                ws_message = create_message_update(
                    session_id=self.session_id,
                    message_type=message_type,
                    content=content,
                    agent=agent
                )
                
                await self.websocket_manager.broadcast_to_session(
                    self.session_id, ws_message.dict()
                )
                
            except Exception as e:
                logger.warning(f"Error processing message: {e}")
                
    async def _handle_agent_status(self, chunk: Dict[str, Any]):
        """Handle agent status updates from chunk"""
        # Check for specific agent completions based on report presence
        agent_reports = {
            "market_report": "Market Analyst",
            "sentiment_report": "Social Analyst", 
            "news_report": "News Analyst",
            "fundamentals_report": "Fundamentals Analyst",
            "investment_plan": "Research Manager",
            "trader_investment_plan": "Trader",
            "final_trade_decision": "Portfolio Manager"
        }
        
        for report_key, agent_name in agent_reports.items():
            if report_key in chunk:
                # Agent completed
                await self._update_agent_status(agent_name, AgentStatus.COMPLETED)
                
        # Handle current agent detection from messages
        if "messages" in chunk and chunk["messages"]:
            last_message = chunk["messages"][-1]
            agent = self._determine_agent_from_message(last_message)
            if agent and agent != self.current_agent:
                # New agent started
                if self.current_agent:
                    await self._update_agent_status(self.current_agent, AgentStatus.COMPLETED)
                await self._update_agent_status(agent, AgentStatus.IN_PROGRESS)
                self.current_agent = agent
                
    async def _handle_reports(self, chunk: Dict[str, Any]):
        """Handle report updates from chunk"""
        report_sections = [
            "market_report", "sentiment_report", "news_report", 
            "fundamentals_report", "investment_plan", "trader_investment_plan",
            "final_trade_decision"
        ]
        
        for section in report_sections:
            if section in chunk:
                content = chunk[section]
                if content:
                    # Update session
                    await self.session_manager.update_report_section(
                        self.session_id, section, content
                    )
                    
                    # Broadcast update
                    ws_message = create_report_update_message(
                        session_id=self.session_id,
                        section=section,
                        content=content,
                        agent=self._get_agent_for_report(section),
                        is_final=section == "final_trade_decision"
                    )
                    
                    await self.websocket_manager.broadcast_to_session(
                        self.session_id, ws_message.dict()
                    )
                    
    async def _update_agent_status(self, agent: str, status: AgentStatus):
        """Update agent status and broadcast"""
        # Track timing
        now = datetime.now()
        start_time = None
        end_time = None
        
        if status == AgentStatus.IN_PROGRESS:
            self.agent_start_times[agent] = now
            start_time = now
        elif status in [AgentStatus.COMPLETED, AgentStatus.FAILED]:
            start_time = self.agent_start_times.get(agent)
            end_time = now
            
        # Update session
        await self.session_manager.update_agent_status(self.session_id, agent, status)
        
        # Broadcast update
        ws_message = create_agent_status_message(
            session_id=self.session_id,
            agent=agent,
            status=status,
            start_time=start_time,
            end_time=end_time
        )
        
        await self.websocket_manager.broadcast_to_session(
            self.session_id, ws_message.dict()
        )
        
    async def _broadcast_error(self, error_type: str, error_message: str, agent: Optional[str] = None):
        """Broadcast error message"""
        ws_message = create_error_message(
            session_id=self.session_id,
            error_type=error_type,
            error_message=error_message,
            agent=agent
        )
        
        await self.websocket_manager.broadcast_to_session(
            self.session_id, ws_message.dict()
        )
        
    def _extract_content_string(self, content) -> str:
        """Extract string content from message content"""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # Handle list of content blocks
            text_parts = []
            for item in content:
                if isinstance(item, dict) and 'text' in item:
                    text_parts.append(item['text'])
                elif isinstance(item, str):
                    text_parts.append(item)
            return ' '.join(text_parts)
        elif hasattr(content, 'content'):
            return str(content.content)
        else:
            return str(content)
            
    def _determine_agent_from_message(self, message) -> Optional[str]:
        """Determine which agent sent a message"""
        # Try to extract from message metadata
        if hasattr(message, 'name') and message.name:
            return message.name
        elif hasattr(message, 'additional_kwargs'):
            name = message.additional_kwargs.get('name')
            if name:
                return name
                
        # Fallback to content analysis
        content = self._extract_content_string(message.content).lower()
        
        # Simple keyword matching
        agent_keywords = {
            "Market Analyst": ["market", "price", "technical", "chart"],
            "Social Analyst": ["social", "sentiment", "twitter", "reddit"],
            "News Analyst": ["news", "article", "headline", "event"],
            "Fundamentals Analyst": ["financial", "earnings", "revenue", "balance"],
            "Bull Researcher": ["bullish", "positive", "buy", "upside"],
            "Bear Researcher": ["bearish", "negative", "sell", "downside"],
            "Research Manager": ["research", "analysis", "conclusion"],
            "Trader": ["trade", "position", "strategy", "execution"],
            "Portfolio Manager": ["portfolio", "allocation", "decision"]
        }
        
        for agent, keywords in agent_keywords.items():
            if any(keyword in content for keyword in keywords):
                return agent
                
        return None
        
    def _get_agent_for_report(self, section: str) -> Optional[str]:
        """Get agent responsible for report section"""
        section_agents = {
            "market_report": "Market Analyst",
            "sentiment_report": "Social Analyst",
            "news_report": "News Analyst", 
            "fundamentals_report": "Fundamentals Analyst",
            "investment_plan": "Research Manager",
            "trader_investment_plan": "Trader",
            "final_trade_decision": "Portfolio Manager"
        }
        return section_agents.get(section)

class AnalysisService:
    """Thread-safe analysis service"""
    
    def __init__(self, max_concurrent_analyses: int = 5):
        self.max_concurrent_analyses = max_concurrent_analyses
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_analyses)
        self.active_analyses: Dict[str, threading.Event] = {}
        self.analysis_lock = asyncio.Lock()
        
    async def start_analysis(self, session_id: str, request: AnalysisRequest) -> bool:
        """Start analysis for a session"""
        async with self.analysis_lock:
            if len(self.active_analyses) >= self.max_concurrent_analyses:
                logger.warning(f"Maximum concurrent analyses reached, rejecting session {session_id}")
                return False
                
            # Create cancellation event
            cancel_event = threading.Event()
            self.active_analyses[session_id] = cancel_event
            
        # Start analysis in background
        asyncio.create_task(self._run_analysis(session_id, request, cancel_event))
        return True
        
    async def cancel_analysis(self, session_id: str) -> bool:
        """Cancel running analysis"""
        if session_id in self.active_analyses:
            self.active_analyses[session_id].set()
            logger.info(f"Cancelled analysis for session {session_id}")
            return True
        return False
        
    async def _run_analysis(self, session_id: str, request: AnalysisRequest, cancel_event: threading.Event):
        """Run analysis in background thread"""
        session_manager = await get_session_manager()
        stream_handler = AnalysisStreamHandler(session_id)
        await stream_handler.initialize()
        
        try:
            # Mark analysis as started
            await session_manager.start_analysis(session_id)
            
            # Run analysis in thread pool
            loop = asyncio.get_event_loop()
            final_result = await loop.run_in_executor(
                self.executor,
                self._execute_analysis,
                session_id,
                request,
                cancel_event,
                stream_handler
            )
            
            if final_result and not cancel_event.is_set():
                # Analysis completed successfully
                final_decision = final_result.get("final_trade_decision")
                await session_manager.complete_analysis(session_id, final_decision)
                
                # Broadcast completion
                ws_message = create_analysis_complete_message(
                    session_id=session_id,
                    final_trade_decision=final_decision,
                    summary="Analysis completed successfully"
                )
                
                websocket_manager = await get_websocket_manager()
                await websocket_manager.broadcast_to_session(session_id, ws_message.dict())
                
            elif cancel_event.is_set():
                # Analysis was cancelled
                await session_manager.cancel_analysis(session_id)
            else:
                # Analysis failed
                await session_manager.fail_analysis(session_id, "Analysis execution failed")
                
        except Exception as e:
            logger.error(f"Analysis error for session {session_id}: {e}")
            await session_manager.fail_analysis(session_id, str(e))
            await stream_handler._broadcast_error("analysis_execution_error", str(e))
            
        finally:
            # Clean up
            async with self.analysis_lock:
                if session_id in self.active_analyses:
                    del self.active_analyses[session_id]
                    
    def _execute_analysis(self, session_id: str, request: AnalysisRequest, 
                         cancel_event: threading.Event, stream_handler: AnalysisStreamHandler) -> Optional[Dict[str, Any]]:
        """Execute analysis in thread (blocking)"""
        try:
            # Create configuration
            config = DEFAULT_CONFIG.copy()
            config["max_debate_rounds"] = request.research_depth
            
            # Map LLM config
            llm_config = {
                "provider": request.llm_config.provider.value,
                "model": request.llm_config.model,
                "temperature": request.llm_config.temperature
            }
            
            # Create TradingAgentsGraph
            selected_analysts = [analyst.value for analyst in request.selected_analysts]
            graph = TradingAgentsGraph(
                selected_analysts=selected_analysts,
                debug=False,
                config=config
            )
            
            # Create initial state
            init_agent_state = graph.propagator.create_initial_state(
                request.ticker, request.trade_date
            )
            
            # Stream analysis
            final_state = None
            for chunk in graph.graph.stream(init_agent_state, config={"recursion_limit": 50}):
                if cancel_event.is_set():
                    logger.info(f"Analysis cancelled for session {session_id}")
                    return None
                    
                # Process chunk asynchronously
                asyncio.run_coroutine_threadsafe(
                    stream_handler.handle_chunk(chunk),
                    asyncio.get_event_loop()
                ).result()
                
                final_state = chunk
                
            return final_state
            
        except Exception as e:
            logger.error(f"Analysis execution error: {e}")
            raise

# Global analysis service instance
analysis_service = AnalysisService()

def get_analysis_service() -> AnalysisService:
    """Get the global analysis service instance"""
    return analysis_service
