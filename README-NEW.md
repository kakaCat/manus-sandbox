# Manus AI Sandbox - Complete Implementation
# Based on ai-manus project with LangChain + LangGraph enhancements

## Overview

This repository contains a complete implementation of the Manus AI Agent sandbox environment, featuring:

- **Frontend**: Vue.js 3 + TypeScript chat interface
- **Backend**: FastAPI + LangChain + LangGraph workflow engine
- **Sandbox**: Docker-based isolated execution environment
- **Tools**: Browser automation, shell commands, file operations, web search

## Architecture

```
Frontend (Vue 3) ←→ Backend (FastAPI) ←→ Docker Sandbox (Ubuntu)
     ↓                      ↓                      ↓
   Chat UI             LangGraph Workflow      Tool Execution
   Sessions              Agent Services         Isolated Environment
   Real-time Events      MongoDB + Redis       Browser + Shell + Files
```

## Quick Start

### 1. Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### 2. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd manus-sandbox

# Configure environment
cp .env.example .env
# Edit .env with your API keys (OPENAI_API_KEY, etc.)
```

### 3. Start Services
```bash
# Option 1: Using the startup script (recommended)
./start-new-sandbox.sh

# Option 2: Manual startup
cd backend-new && pip install -r requirements.txt
cd ../frontend-new && npm install

# Start backend
cd backend-new && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Start frontend
cd frontend-new && npm run dev &
```

### 4. Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Features

### AI Agent Capabilities
- **Planning**: Breaks down complex tasks into steps
- **Execution**: Uses LangChain tools to perform actions
- **Reflection**: Evaluates results and adjusts approach
- **Memory**: Maintains session context across interactions

### Available Tools
- 🌐 **Browser**: Navigate websites, extract content
- 💻 **Shell**: Execute system commands in sandbox
- 📁 **File**: Read/write files in isolated environment
- 🔍 **Search**: Web search with multiple providers

### Sandbox Environment
- **Isolation**: Each session gets dedicated container
- **Security**: Restricted execution environment
- **Persistence**: MongoDB for session data, Redis for caching
- **Cleanup**: Automatic container lifecycle management

## Development

### Project Structure
```
manus-sandbox/
├── frontend-new/          # Vue.js frontend
├── backend-new/           # FastAPI backend
├── start-new-sandbox.sh   # Development startup script
├── docker-compose.yml     # Production deployment
└── README.md             # This file
```

### Backend Architecture
- **Domain Layer**: Agents, tools, graphs, models
- **Application Layer**: Services, session management
- **Infrastructure Layer**: Docker, MongoDB, Redis, LLM
- **Interface Layer**: REST API, schemas

### Frontend Architecture
- **Vue 3 Composition API**: Modern reactive framework
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Server-Sent Events**: Real-time agent communication

## API Reference

### Sessions
- `PUT /api/v1/sessions` - Create new session
- `GET /api/v1/sessions` - List all sessions
- `GET /api/v1/sessions/{id}` - Get session details
- `DELETE /api/v1/sessions/{id}` - Delete session

### Chat
- `POST /api/v1/sessions/{id}/chat` - Send message (SSE stream)
- `POST /api/v1/sessions/{id}/stop` - Stop running session

## Configuration

### Environment Variables
```bash
# LLM Configuration
OPENAI_API_KEY=your_key_here
OPENAI_API_BASE=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat

# Database
MONGODB_URI=mongodb://localhost:27017
REDIS_HOST=localhost

# Sandbox
SANDBOX_IMAGE=simpleyyt/manus-sandbox
SANDBOX_TTL_MINUTES=30

# Search
SEARCH_PROVIDER=bing
```

## Deployment

### Docker Compose (Recommended)
```bash
docker-compose up -d
```

### Manual Deployment
```bash
# Build images
docker build -t manus-frontend ./frontend-new
docker build -t manus-backend ./backend-new

# Run services
docker run -d -p 8000:8000 manus-backend
docker run -d -p 5173:5173 manus-frontend
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Based on [ai-manus](https://github.com/Simpleyyt/ai-manus) project
- Inspired by the original Manus AI Agent implementation
- Built with LangChain, LangGraph, and modern web technologies