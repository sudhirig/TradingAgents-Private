import openai
import json
import asyncio
from typing import List, Dict, Any, AsyncGenerator
import re
from datetime import datetime
import os

class StrategyGenerator:
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
    async def stream_nl_to_backtrader(self, description: str, symbols: List[str], parameters: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream AI code generation in real-time like Statis Fund"""
        
        prompt = self._build_strategy_prompt(description, symbols, parameters)
        
        try:
            # Stream the OpenAI response
            stream = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                stream=True,
                max_tokens=2000
            )
            
            code_chunks = []
            chunk_count = 0
            
            async for chunk in stream:
                chunk_count += 1
                if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    code_chunks.append(content)
                    
                    # Yield streaming updates
                    yield {
                        "code_partial": content,
                        "code_full": ''.join(code_chunks),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                # Safety check to prevent infinite loops
                if chunk_count > 1000:
                    yield {"error": "Stream too long, terminating"}
                    break
                    
            # Final validation and cleanup
            final_code = ''.join(code_chunks)
            validated_code = self._validate_strategy_code(final_code)
            
            yield {
                "code": validated_code,
                "status": "validation_complete",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            yield {"error": f"OpenAI streaming error: {str(e)}"}
    
    async def nl_to_backtrader(self, description: str, symbols: List[str], parameters: Dict[str, Any]) -> str:
        """Convert natural language to Backtrader strategy code (non-streaming)"""
        
        prompt = self._build_strategy_prompt(description, symbols, parameters)
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000
        )
        
        code = response.choices[0].message.content
        validated_code = self._validate_strategy_code(code)
        
        return validated_code
    
    def _build_strategy_prompt(self, description: str, symbols: List[str], parameters: Dict[str, Any]) -> str:
        """Build comprehensive prompt for strategy generation"""
        
        return f"""
        Convert this trading strategy description into professional Backtrader Python code for USA stocks:
        
        Strategy Description: {description}
        Target Symbols: {symbols}
        Parameters: {parameters}
        
        Requirements:
        1. Create a class inheriting from bt.Strategy with proper __init__ method
        2. Use USA stock symbols (SPY, AAPL, TSLA, QQQ, etc.)
        3. Include comprehensive risk management:
           - Stop loss (2-5% maximum loss per trade)
           - Position sizing (max 10% of portfolio per position)
           - Maximum drawdown protection
        4. Add proper logging with self.log() for all trades
        5. Handle edge cases (insufficient data, market gaps, etc.)
        6. Use yfinance data format with proper OHLCV access
        7. Include technical indicators from backtrader.indicators
        8. Add entry and exit conditions with clear logic
        9. Include proper imports and class structure
        10. Add comments explaining the strategy logic
        
        Available Indicators: SMA, EMA, RSI, MACD, BollingerBands, Stochastic, ATR, ADX
        
        Return ONLY the Python code with proper class structure, no explanations or markdown.
        """
    
    def _validate_strategy_code(self, code: str) -> str:
        """Comprehensive validation and sanitization of generated strategy code"""
        
        # Remove dangerous imports/functions
        dangerous_patterns = [
            r'import\s+os(?!\w)',
            r'import\s+sys(?!\w)', 
            r'import\s+subprocess',
            r'exec\s*\(',
            r'eval\s*\(',
            r'__import__',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'raw_input\s*\(',
            r'compile\s*\(',
            r'globals\s*\(',
            r'locals\s*\(',
            r'vars\s*\(',
            r'dir\s*\(',
            r'delattr',
            r'setattr',
            r'hasattr'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                raise ValueError(f"Dangerous code pattern detected: {pattern}")
        
        # Ensure required imports are present
        required_imports = [
            "import backtrader as bt",
            "import pandas as pd", 
            "import numpy as np"
        ]
        
        for import_stmt in required_imports:
            if import_stmt not in code:
                code = import_stmt + "\n" + code
        
        # Validate strategy class exists
        if not re.search(r'class\s+\w+\s*\(\s*bt\.Strategy\s*\)', code):
            raise ValueError("No valid Strategy class inheriting from bt.Strategy found")
        
        # Ensure basic methods exist
        if 'def __init__' not in code:
            raise ValueError("Strategy class must have __init__ method")
            
        if 'def next' not in code:
            raise ValueError("Strategy class must have next() method")
        
        # Add safety wrapper
        safety_header = '''
# Auto-generated strategy with safety controls
import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime

'''
        
        if not code.startswith(safety_header.strip()):
            code = safety_header + code
        
        return code
