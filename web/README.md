# 🤖 TradingAgents Web Frontend - Multi-Agent Analysis Platform

A cutting-edge real-time web interface for the TradingAgents multi-agent financial analysis system. Built with modern technologies for professional trading analysis workflows.

## ✨ Key Features

### 🔄 Real-time Multi-Agent Analysis
- **12 Specialized Agents**: Market, Social, News, Fundamentals analysts + Research, Trading, Risk teams
- **Live WebSocket Updates**: Real-time agent status, messages, and tool calls
- **Team-based Workflow**: Sequential team execution (Analyst → Research → Trading → Risk → Portfolio)
- **Progress Visualization**: Live agent status grid with animations and indicators

### 📊 Interactive Dashboard
- **Modern CLI-style Interface**: Professional terminal-inspired design
- **System Metrics**: Real-time statistics and performance monitoring
- **Message Feed**: Live filtering by type (info, success, warning, error)
- **Tool Call Viewer**: Expandable details with parameter/result viewing

### 🚀 Performance & Scalability
- **Message Batching**: Efficient WebSocket communication with batching
- **Virtual Scrolling**: Handle large message feeds efficiently
- **Memory Management**: Automatic cleanup of old sessions and messages
- **Auto-reconnection**: Robust WebSocket connection management

### 🔒 Enterprise Security
- **Rate Limiting**: Token bucket algorithm with endpoint-specific rules
- **Input Validation**: Comprehensive sanitization of all inputs
- **Security Headers**: CORS, CSP, and security middleware
- **Session Management**: Secure session handling with timeouts

## 📋 Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (for deployment)
- Chrome/Chromium (for E2E tests)

## 🛠️ Quick Start

### Development Setup

1. **Environment Configuration**
   ```bash
   cd /Users/Gautam/TradingAgents/web
   
   # Setup environment variables
   cp .env.example .env
   # Edit .env with your API keys:
   # OPENAI_API_KEY=your_openai_key
   # ANTHROPIC_API_KEY=your_anthropic_key
   # GROQ_API_KEY=your_groq_key
   ```

2. **Backend Setup & Start**
   ```bash
   cd backend
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Start development server
   python -m app.main
   # 🚀 Backend running on http://localhost:8001
   # 📚 API docs at http://localhost:8001/docs
   ```

3. **Frontend Setup & Start**
   ```bash
   cd frontend
   
   # Install dependencies
   npm install
   
   # Start development server
   npm run dev
   # 🚀 Frontend running on http://localhost:5173
   ```

4. **Verify Installation**
   ```bash
   # Test backend health
   curl http://localhost:8001/health
   
   # Test WebSocket connection
   # Open browser to http://localhost:5173 and start analysis
   ```

### Docker Deployment

1. **Production Deployment**
   ```bash
   # Set environment variables
   export OPENAI_API_KEY=your_key_here
   export ANTHROPIC_API_KEY=your_key_here
   export GROQ_API_KEY=your_key_here
   
   # Deploy with Docker Compose
   docker-compose up -d
   
   # Access at http://localhost
   ```

2. **Health Checks**
   ```bash
   # Check backend health
   curl http://localhost:8003/health
   
   # Check frontend
   curl http://localhost/health
   ```

## 🧪 Testing

### Run All Tests
```bash
cd tests
python run_all_tests.py
```

### Individual Test Suites
```bash
# E2E Tests
python tests/e2e/test_full_analysis_flow.py

# Load Tests
python tests/load/test_concurrent_load.py

# Backend Tests
cd backend && python -m pytest

# Frontend Tests
cd frontend && npm test
```

## 📊 Architecture

### Backend (FastAPI)
- **WebSocket Manager**: Thread-safe connection management with session tracking
- **Analysis Service**: Integration with TradingAgents core system
- **Performance Utils**: Message batching, memory management, metrics collection
- **Security Layer**: Rate limiting, input validation, security headers

### Frontend (React + TypeScript)
- **State Management**: Zustand with persistence
- **Real-time Updates**: WebSocket integration with auto-reconnection
- **UI Components**: Responsive design with Tailwind CSS
- **Performance**: Virtual scrolling, optimized rendering

### Key Components

```
web/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models/              # Pydantic data models
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   ├── utils/               # Performance & security utilities
│   │   └── middleware/          # Security middleware
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── store/               # Zustand state management
│   │   ├── hooks/               # Custom React hooks
│   │   └── types/               # TypeScript definitions
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── tests/
│   ├── e2e/                     # End-to-end tests
│   ├── load/                    # Load testing
│   └── run_all_tests.py         # Master test runner
├── docker-compose.yml
└── .env.example
```

## 🔧 Configuration

### Environment Variables

```bash
# API Keys (Required)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GROQ_API_KEY=your_groq_api_key

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8003
CORS_ORIGINS=http://localhost:3000,http://localhost:5174

# Performance Settings
MAX_WEBSOCKET_CONNECTIONS=100
MESSAGE_BATCH_SIZE=10
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

### API Endpoints

- `GET /health` - Health check
- `GET /api/config/analysts` - Available analysts
- `GET /api/config/llm-providers` - LLM providers
- `POST /api/analysis/start` - Start analysis
- `WS /ws/{session_id}` - WebSocket connection
- `GET /api/metrics/performance` - Performance metrics

## 📈 Performance Features

### Backend Optimizations
- **Message Batching**: Groups WebSocket messages for efficient transmission
- **Memory Management**: Automatic cleanup of old sessions and messages
- **Rate Limiting**: Token bucket algorithm with endpoint-specific rules
- **Performance Monitoring**: Real-time metrics collection and reporting

### Frontend Optimizations
- **Virtual Scrolling**: Handles large message feeds efficiently
- **State Persistence**: Saves UI preferences and session data
- **Auto-reconnection**: Robust WebSocket connection management
- **Optimized Rendering**: React.memo and useMemo for performance

## 🔒 Security Features

- **Rate Limiting**: Prevents API abuse with configurable limits
- **Input Validation**: Comprehensive sanitization of all inputs
- **Security Headers**: CORS, CSP, and other security headers
- **Session Management**: Secure session handling with timeouts
- **HTTPS Ready**: Production configuration with SSL support

## 🚀 Deployment

### Docker Production Deployment

1. **Build and Deploy**
   ```bash
   # Build images
   docker-compose build
   
   # Deploy services
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   ```

2. **Scaling**
   ```bash
   # Scale backend workers
   docker-compose up -d --scale backend=3
   ```

3. **Monitoring**
   ```bash
   # Check service health
   docker-compose ps
   
   # View performance metrics
   curl http://localhost/api/metrics/performance
   ```

### Manual Deployment

1. **Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8003 --workers 4
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   # Serve dist/ with nginx or similar
   ```

## 🧪 Testing Strategy

### Test Coverage
- **Unit Tests**: Backend services and utilities
- **Component Tests**: React component functionality
- **Integration Tests**: API endpoints and WebSocket communication
- **E2E Tests**: Complete user workflows with browser automation
- **Load Tests**: Performance under concurrent load
- **Security Tests**: Rate limiting and input validation

### Test Execution
```bash
# Run comprehensive test suite
python tests/run_all_tests.py

# Results saved to comprehensive_test_results.json
```

## 📚 Development Guide

### Adding New Features

1. **Backend API Endpoint**
   ```python
   # Add to app/routers/
   @router.get("/new-endpoint")
   async def new_endpoint():
       return {"data": "response"}
   ```

2. **Frontend Component**
   ```tsx
   // Add to src/components/
   export const NewComponent: React.FC = () => {
       return <div>New Feature</div>;
   };
   ```

3. **WebSocket Message Type**
   ```python
   # Backend: Add to models/websocket.py
   class NewMessageType(WebSocketMessage):
       type: Literal["new_message"] = "new_message"
       data: Dict[str, Any]
   ```

### Performance Monitoring

Access real-time metrics at:
- Backend: `http://localhost:8003/api/metrics/performance`
- Frontend: Performance Monitor component in dashboard

### Debugging

1. **Backend Logs**
   ```bash
   tail -f web_backend.log
   ```

2. **Frontend DevTools**
   - React DevTools for component inspection
   - Network tab for WebSocket messages
   - Console for error logging

## 🤝 Contributing

1. Follow the existing code structure and patterns
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass before submitting

## 📄 License

This project is part of the TradingAgents system. See LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check backend is running on port 8003
   - Verify CORS configuration
   - Check firewall settings

2. **Frontend Build Errors**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify all dependencies are installed

3. **Backend Import Errors**
   - Ensure Python path includes project root
   - Check all required packages are installed
   - Verify environment variables are set

4. **Docker Issues**
   - Check Docker daemon is running
   - Verify port availability
   - Check environment variable configuration

### Getting Help

- Check the logs for detailed error messages
- Run the test suite to identify issues
- Review the API documentation at `/docs`
- Check performance metrics for bottlenecks

---

**Built with ❤️ for real-time trading analysis**
