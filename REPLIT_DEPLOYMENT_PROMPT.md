# 🚀 **Complete Replit Deployment Guide: Trading Platform Microservices**

## **🎯 Project Overview**

Deploy a complete trading analysis platform with **two independent microservices** running on separate ports:

### **📊 Microservice Architecture**

1. **Statis Fund Replica** (Internal: 8000 → External: 80) - AI-Powered Strategy Platform
   - Advanced backtesting with 122+ technical indicators
   - Real-time AI strategy generation with streaming
   - Professional trading interface with 29 React components
   - 15+ performance analyzers (Sharpe, Sortino, Calmar ratios)
   - 8+ advanced order types (Market, Limit, Stop, Trailing Stop)

2. **TradingAgents Web** (Internal: 8001 → External: 8001) - Multi-Agent Analysis Platform  
   - 12 specialized AI agents across 5 teams
   - Real-time WebSocket streaming with live updates
   - Team-based workflow execution (Analyst→Research→Trading→Risk→Portfolio)
   - Professional CLI-style interface with React + TypeScript
   - Comprehensive data sources (yfinance, Reddit, news APIs)

---

## **🔧 Replit Port System Understanding**

### **How Replit Ports Work**
Replit uses a **localPort → externalPort** mapping system:
- **localPort**: Internal port your service binds to (e.g., 8000)
- **externalPort**: External port accessible via web (e.g., 80)
- **No localhost binding**: Services bind to `0.0.0.0`, not `localhost`
- **Automatic SSL**: All external ports get HTTPS automatically

### **Port Mapping Configuration**
```toml
# .replit file configuration
[[ports]]
localPort = 8000    
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://*.repl.co",  
    "https://*.replit.dev",  
]

[[ports]]
localPort = 8001    
externalPort = 8001 
exposeLocalhost = false
```

### **System Requirements**
- **Python**: 3.11+ (for modern async/await and type hints)
- **Node.js**: 20+ (for React 18+ and modern JavaScript features)
- **Memory**: Minimum 2GB RAM (4GB+ recommended for both services)
- **Storage**: ~500MB for dependencies + data cache
- **Network**: Outbound HTTPS for API calls (OpenAI, yfinance, Reddit)

### **Replit Plan Recommendations**
- **Free Tier**: Basic testing only (512MB RAM limitation)
- **Hacker Plan**: $7/month - Recommended for development (4GB RAM)
- **Pro Plan**: $20/month - Production ready (8GB RAM, always-on)

### **External Access URLs**
```bash
# After deployment, your services will be available at:
Statis Fund Backend:     https://[repl-name]--[username].repl.co
TradingAgents Backend:   https://[repl-name]--[username].repl.co:8001
Statis Fund Frontend:    https://[repl-name]--[username].repl.co:3000
TradingAgents Frontend:  https://[repl-name]--[username].repl.co:3001
```

## **Alternative: Direct Upload Instructions**

If GitHub import doesn't work, here's what to upload to Replit:

### **Essential Files to Upload**:
```
📁 TradingAgents/
├── 📄 .replit                      
├── 📄 replit.nix                        
├── 📄 main.py                           
├── 📄 requirements.txt                  
├── 📄 pyproject.toml                    
├── 📁 tradingagents/                    
├── 📁 cli/                              
├── 📁 web/                              
├── 📄 AI_HEDGE_FUND_INTEGRATION_GUIDE.md 
├── 📄 INDIA_STOCK_DATA_MAPPING.md       
└── 📄 REPLIT_DEPLOYMENT_GUIDE.md        
├── 📄 AI_HEDGE_FUND_INTEGRATION_GUIDE.md # Integration guide
├── 📄 INDIA_STOCK_DATA_MAPPING.md       # Indian stocks guide
└── 📄 REPLIT_DEPLOYMENT_GUIDE.md        # Deployment guide
```

### **Upload Steps**:
1. **Create New Repl** → Choose "Python" template
2. **Upload Folder** → Drag entire "TradingAgents" folder
3. **Set Environment Variables** in Secrets tab:
   ```
   OPENAI_API_KEY=your-key
   REDDIT_CLIENT_ID=your-reddit-id
   REDDIT_CLIENT_SECRET=your-reddit-secret
   FINNHUB_API_KEY=your-finnhub-key
   ```
4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Test CLI**:
   ```bash
   python main.py --ticker RELIANCE.NS,TCS.NS
   ```
6. **Start Web Interface**:
   ```bash
   cd web/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## **Quick Test Commands**

Once deployed, test with these commands:

### **US Stocks Test**:
```bash
python main.py --ticker AAPL,MSFT,NVDA
```

### **Indian Stocks Test**:
```bash
python main.py --ticker RELIANCE.NS,TCS.NS,INFY.NS --market india
```

### **Web Interface Test**:
```bash
cd web/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### **Parallel Systems Test**:
```bash
# This will run both AI-Hedge-Fund and TradingAgents side-by-side
python comparison/parallel_analysis.py --ticker AAPL,RELIANCE.NS
```

## **Expected Results**

✅ **Successful Deployment When**:
- CLI analyzes both US and Indian stocks
- Web interface shows real-time agent updates
- Indian stocks display in INR currency
- Both systems provide investment recommendations
- Comparison dashboard shows side-by-side results
- WebSocket streaming works for live updates

## **Troubleshooting**

If you encounter issues:

1. **Memory Errors**: Upgrade to Hacker plan (4GB RAM)
2. **Import Errors**: Check Python path in `.replit` file
3. **API Errors**: Verify environment variables in Secrets
4. **Port Conflicts**: Use port 8000 for backend, auto-assigned for frontend

Your Replit deployment will provide a comprehensive trading analysis platform with both legendary investor insights and structured multi-agent workflows! 🚀📈
