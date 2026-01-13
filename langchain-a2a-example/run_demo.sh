#!/bin/bash

# LangChain A2A 示例启动脚本

echo "🚀 启动 LangChain A2A 通信示例"
echo ""

# 检查 Python
if ! command -v python &> /dev/null; then
    echo "❌ Python 未安装，请先安装 Python 3.10+"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
python -c "
try:
    import a2a
    print('✅ a2a-sdk 已安装')
except ImportError:
    print('❌ a2a-sdk 未安装，请运行: pip install -r requirements.txt')

try:
    import langchain
    print('✅ langchain 已安装')
except ImportError:
    print('❌ langchain 未安装，请运行: pip install -r requirements.txt')
"

# 检查环境变量
if [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "⚠️  未设置 OPENAI_API_KEY 环境变量"
    echo "   请设置环境变量或创建 .env 文件"
    echo "   示例: export OPENAI_API_KEY='your-key-here'"
    echo ""
fi

# 运行示例
echo ""
echo "🎯 运行示例..."
python examples/langchain_a2a_demo.py