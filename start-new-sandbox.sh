#!/bin/bash

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=5173
MONGO_PORT=27017
REDIS_PORT=6379

echo -e "${BLUE}🚀 启动 Manus AI Agent (LangChain + LangGraph)${NC}"
echo ""

# 检查依赖
check_dependencies() {
    echo -e "${YELLOW}📋 Checking dependencies...${NC}"

    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not installed${NC}"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose not installed${NC}"
        exit 1
    fi

    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js not installed${NC}"
        exit 1
    fi

    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 not installed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Dependencies check passed${NC}"
    echo ""
}

# 检查端口占用
check_ports() {
    echo -e "${YELLOW}🔍 Checking port availability...${NC}"

    local ports=($BACKEND_PORT $FRONTEND_PORT $MONGO_PORT $REDIS_PORT)
    local occupied_ports=()

    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            occupied_ports+=($port)
        fi
    done

    if [ ${#occupied_ports[@]} -ne 0 ]; then
        echo -e "${RED}❌ Ports occupied: ${occupied_ports[*]}${NC}"
        echo "Stop occupying processes or change port configuration"
        exit 1
    fi

    echo -e "${GREEN}✅ Ports available${NC}"
    echo ""
}

# 启动 MongoDB 和 Redis
start_infrastructure() {
    echo -e "${YELLOW}🐳 Starting infrastructure services...${NC}"

    docker run -d \
        --name manus-mongo \
        -p $MONGO_PORT:27017 \
        --rm \
        mongo:7.0 \
        > /dev/null 2>&1

    docker run -d \
        --name manus-redis \
        -p $REDIS_PORT:6379 \
        --rm \
        redis:7.0 \
        > /dev/null 2>&1

    echo -e "${GREEN}✅ Infrastructure services started${NC}"
    echo ""
}

# 启动后端
start_backend() {
    echo -e "${YELLOW}🔧 Starting backend service...${NC}"

    cd backend-new

    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️  .env file not found, creating from example...${NC}"
        cp .env.example .env
        echo "Please edit backend-new/.env with your API keys"
    fi

    echo "Installing Python dependencies..."
    pip install -r requirements.txt > /dev/null 2>&1

    uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!

    cd ..
    echo -e "${GREEN}✅ Backend service started${NC}"
    echo ""
}

# 启动前端
start_frontend() {
    echo -e "${YELLOW}🎨 Starting frontend service...${NC}"

    cd frontend-new

    echo "Installing Node.js dependencies..."
    npm install > /dev/null 2>&1

    npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!

    cd ..
    echo -e "${GREEN}✅ Frontend service started${NC}"
    echo ""
}

# 等待服务就绪
wait_for_services() {
    echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"

    local retries=30
    while [ $retries -gt 0 ]; do
        if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend ready${NC}"
            break
        fi
        sleep 2
        retries=$((retries-1))
    done

    if [ $retries -eq 0 ]; then
        echo -e "${RED}❌ Backend startup failed${NC}"
        exit 1
    fi

    retries=30
    while [ $retries -gt 0 ]; do
        if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Frontend ready${NC}"
            break
        fi
        sleep 2
        retries=$((retries-1))
    done

    if [ $retries -eq 0 ]; then
        echo -e "${RED}❌ Frontend startup failed${NC}"
        exit 1
    fi

    echo ""
}

# 显示服务信息
show_info() {
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}✅ All services started successfully!${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
    echo -e "${BLUE}📍 Service URLs:${NC}"
    echo "  - Frontend: http://localhost:$FRONTEND_PORT"
    echo "  - Backend API: http://localhost:$BACKEND_PORT"
    echo "  - API Docs: http://localhost:$BACKEND_PORT/docs"
    echo ""
    echo -e "${BLUE}📊 Infrastructure:${NC}"
    echo "  - MongoDB: localhost:$MONGO_PORT"
    echo "  - Redis: localhost:$REDIS_PORT"
    echo ""
    echo -e "${BLUE}📝 Logs:${NC}"
    echo "  - Backend: logs/backend.log"
    echo "  - Frontend: logs/frontend.log"
    echo ""
    echo -e "${BLUE}💡 Tips:${NC}"
    echo "  - Code changes auto-reload"
    echo "  - Press Ctrl+C to stop"
    echo "  - View logs: tail -f logs/backend.log"
    echo ""
}

# 清理函数
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping all services...${NC}"

    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    docker stop manus-mongo manus-redis 2>/dev/null

    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

main() {
    mkdir -p logs

    check_dependencies
    check_ports
    start_infrastructure
    start_backend
    start_frontend
    wait_for_services
    show_info

    trap cleanup INT TERM

    echo -e "${BLUE}Press Ctrl+C to stop services...${NC}"
    wait
}

main