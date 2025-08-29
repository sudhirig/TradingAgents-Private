from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import json
import asyncio
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import yfinance as yf
import pandas as pd
import backtrader as bt
import openai
import os
from dotenv import load_dotenv

# Import our service layer
from services.strategy_generator import StrategyGenerator
from services.backtest_engine import BacktestEngine
from models.strategy import StrategyRequest, BacktestRequest, DeployRequest
from models.backtest import BacktestResult

load_dotenv()

app = FastAPI(title="TradingAgents Statis Fund Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai_client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize services
strategy_generator = StrategyGenerator()
backtest_engine = BacktestEngine()

# Global state for ideas count (in production, use database)
user_ideas_count = 3

# Global storage for strategies (in production, use a database)
saved_strategies = {}

# Pydantic Models
class StrategyRequest(BaseModel):
    description: str
    start_date: str
    end_date: str
    mode: str = "Interday"
    ai_model: str = "GPT-4.1-mini"

class BacktestRequest(BaseModel):
    code: str
    symbols: List[str]
    start_date: str
    end_date: str
    initial_cash: float = 100000

@app.get("/")
async def root():
    return {"message": "Statis Fund Replica API", "status": "running"}

@app.post("/api/strategy/generate/stream")
async def generate_strategy_stream(request: StrategyRequest):
    """Stream AI code generation in real-time like Statis Fund"""
    global user_ideas_count
    
    if user_ideas_count <= 0:
        raise HTTPException(status_code=429, detail="Ideas limit reached. Register for free to get 100 free ideas per month.")
    
    async def generate():
        yield "data: {\"status\": \"SSE connection established...\"}\n\n"
        await asyncio.sleep(0.5)
        yield "data: {\"status\": \"This might remain static for non-streaming models\"}\n\n"
        await asyncio.sleep(0.5)
        
        try:
            # Simulate time elapsed with realistic streaming
            for i in range(1, 12):
                yield f"data: {{\"status\": \"Time elapsed: {i}.0s\"}}\n\n"
                await asyncio.sleep(0.8)
            
            yield "data: {\"status\": \"Generating strategy code...\"}\n\n"
            await asyncio.sleep(1)
            
            # Generate strategy code using OpenAI with streaming
            prompt = f"""
            Convert this trading strategy description into Backtrader Python code for USA stocks:
            
            Description: {request.description}
            
            Requirements:
            1. Create a class inheriting from bt.Strategy
            2. Use proper Backtrader syntax for USA stocks (SPY, AAPL, TSLA, etc.)
            3. Include risk management and position sizing
            4. Add logging for debugging
            5. Handle multiple data feeds if needed
            6. Use yfinance data format
            7. Include proper imports and class structure
            
            Return only the Python code, no explanations.
            """
            
            # Stream the OpenAI response
            try:
                stream = await openai_client.chat.completions.create(
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
                        # Stream partial code updates
                        partial_code = ''.join(code_chunks)
                        yield f"data: {{\"code_partial\": {json.dumps(content)}, \"code_full\": {json.dumps(partial_code)}}}\n\n"
                        await asyncio.sleep(0.05)
                    
                    # Safety check to prevent infinite loops
                    if chunk_count > 1000:
                        yield f"data: {{\"error\": \"Stream too long, terminating\"}}\n\n"
                        break
                        
            except Exception as stream_error:
                yield f"data: {{\"error\": \"OpenAI streaming error: {str(stream_error)}\"}}\n\n"
                return
            
            # Final code
            final_code = ''.join(code_chunks)
            yield f"data: {{\"code\": {json.dumps(final_code)}}}\n\n"
            yield "data: {\"status\": \"content.done\"}\n\n"
            
            # Decrement ideas count
            user_ideas_count -= 1
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive"})

@app.post("/api/strategy/generate")
async def generate_strategy(request: StrategyRequest):
    """Non-streaming strategy generation"""
    global user_ideas_count
    
    if user_ideas_count <= 0:
        raise HTTPException(status_code=429, detail="Ideas limit reached")
    
    try:
        prompt = f"""
        Convert this trading strategy description into Backtrader Python code for USA stocks:
        
        Description: {request.description}
        
        Requirements:
        1. Create a class inheriting from bt.Strategy
        2. Use proper Backtrader syntax for USA stocks
        3. Include risk management and position sizing
        4. Add logging for debugging
        
        Return only the Python code, no explanations.
        """
        
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        code = response.choices[0].message.content
        user_ideas_count -= 1
        
        return {"success": True, "code": code, "ideas_remaining": user_ideas_count}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backtest/run")
async def run_backtest(request: BacktestRequest):
    """Execute backtest with generated strategy"""
    try:
        # Initialize Cerebro
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(request.initial_cash)
        cerebro.broker.setcommission(commission=0.001)  # 0.1% commission
        
        # Download data for symbols
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()
        
        for symbol in request.symbols:
            data = yf.download(symbol, start=start_date, end=end_date, auto_adjust=True, progress=False)
            if not data.empty:
                data_feed = bt.feeds.PandasData(dataname=data, name=symbol)
                cerebro.adddata(data_feed)
        
        # Load strategy from code
        strategy_class = load_strategy_from_code(request.code)
        cerebro.addstrategy(strategy_class)
        
        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        
        # Run backtest
        results = cerebro.run()
        final_value = cerebro.broker.getvalue()
        
        # Extract results
        strategy = results[0]
        sharpe = strategy.analyzers.sharpe.get_analysis().get('sharperatio', 0)
        drawdown = strategy.analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 0)
        returns = strategy.analyzers.returns.get_analysis().get('rtot', 0)
        
        return {
            "success": True,
            "result": {
                "initial_cash": request.initial_cash,
                "final_value": final_value,
                "total_return": (final_value - request.initial_cash) / request.initial_cash * 100,
                "sharpe_ratio": sharpe or 0,
                "max_drawdown": drawdown or 0,
                "symbols": request.symbols
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def load_strategy_from_code(code: str):
    """Safely load strategy class from code string"""
    import types
    
    # Create a new module
    module = types.ModuleType("user_strategy")
    
    # Define safe builtins
    safe_builtins = {
        '__builtins__': {
            'len': len, 'range': range, 'min': min, 'max': max, 'abs': abs,
            'round': round, 'sum': sum, 'any': any, 'all': all, 'print': print
        }
    }
    
    # Add required imports to the code
    full_code = f"""
import backtrader as bt
import pandas as pd
import numpy as np
import yfinance as yf

{code}
"""
    
    # Execute code in safe environment
    exec(full_code, safe_builtins, module.__dict__)
    
    # Find strategy class
    for obj in module.__dict__.values():
        if isinstance(obj, type) and issubclass(obj, bt.Strategy) and obj is not bt.Strategy:
            return obj
            
    raise ValueError("No valid Strategy class found in code")

# Statis Fund API endpoints
@app.get("/data/{ticker}")
async def get_stock_data(ticker: str, start: str, end: str, interval: str = "1d", period: int = 14):
    """Get historical stock data"""
    try:
        data = yf.download(ticker, start=start, end=end, interval=interval, auto_adjust=True, progress=False)
        return {"success": True, "data": data.to_dict('records')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/moving_average/{ticker}")
async def get_moving_average(ticker: str, days: int, start: str, end: str, interval: str = "1d"):
    """Calculate moving average"""
    try:
        data = yf.download(ticker, start=start, end=end, interval=interval, auto_adjust=True, progress=False)
        data[f'MA_{days}'] = data['Close'].rolling(window=days).mean()
        return {"success": True, "data": data[['Close', f'MA_{days}']].to_dict('records')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bollinger_bands/{ticker}")
async def get_bollinger_bands(ticker: str, window: int, start: str, end: str, interval: str = "1d"):
    """Calculate Bollinger Bands"""
    try:
        data = yf.download(ticker, start=start, end=end, interval=interval, auto_adjust=True, progress=False)
        data['MA'] = data['Close'].rolling(window=window).mean()
        data['STD'] = data['Close'].rolling(window=window).std()
        data['Upper'] = data['MA'] + (data['STD'] * 2)
        data['Lower'] = data['MA'] - (data['STD'] * 2)
        return {"success": True, "data": data[['Close', 'MA', 'Upper', 'Lower']].to_dict('records')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/ideas")
async def get_user_ideas():
    """Get remaining ideas count"""
    return {"ideas_remaining": user_ideas_count, "limit": 3}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
