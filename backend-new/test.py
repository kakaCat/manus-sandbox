#!/usr/bin/env python3
"""
Quick test script for Manus AI Agent (LangChain + LangGraph)
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import get_settings
from app.infrastructure.llm.langchain_llm import create_llm
from app.infrastructure.sandbox.docker_sandbox import DockerSandbox
from app.domain.agents.deep_agent import DeepAgent
from app.domain.tools.browser import BrowserTool


async def test_config():
    print("📋 Testing configuration...")
    settings = get_settings()
    print(f"✅ Model: {settings.model_name}")
    print(f"✅ API Base: {settings.openai_api_base}")
    print()


async def test_llm():
    print("🤖 Testing LLM connection...")
    try:
        llm = create_llm()
        response = await llm.ainvoke("Say 'Hello' in one word.")
        print(f"✅ LLM response: {response.content}")
        print()
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        sys.exit(1)


async def test_sandbox():
    print("🐳 Testing sandbox creation...")
    try:
        sandbox = DockerSandbox.create()
        print(f"✅ Sandbox created: {sandbox.id}")
        print(f"✅ Sandbox IP: {sandbox.ip}")
        print(f"✅ Base URL: {sandbox.base_url}")

        health = await sandbox.health_check()
        print(f"✅ Health check: {health}")

        await sandbox.shutdown()
        print("✅ Sandbox shutdown successfully")
        print()
    except Exception as e:
        print(f"❌ Sandbox test failed: {e}")
        sys.exit(1)


async def test_tool():
    print("🔧 Testing LangChain tool...")
    try:
        llm = create_llm()

        print("Creating sandbox...")
        sandbox = DockerSandbox.create()
        await asyncio.sleep(3)

        print("Creating browser tool...")
        browser_tool = BrowserTool(sandbox)

        print("Invoking tool...")
        result = await browser_tool._arun(url="https://example.com")

        print(f"✅ Tool result: {result[:100]}...")

        await sandbox.shutdown()
        print("✅ Tool test completed")
        print()
    except Exception as e:
        print(f"❌ Tool test failed: {e}")
        sys.exit(1)


async def main():
    print("🧪 Manus AI Agent - Quick Test")
    print("=" * 50)
    print()

    await test_config()
    await test_llm()

    print("=" * 50)
    print("✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
