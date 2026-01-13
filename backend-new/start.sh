#!/bin/bash

set -e

echo "🚀 Starting Manus AI Agent (LangChain + LangGraph)..."

if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env with your configuration"
    exit 1
fi

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🔧 Starting server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
