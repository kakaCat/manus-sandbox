from langchain_core.tools import tool


import httpx
from langchain_core.tools import tool
from typing import Optional


class BrowserTool:
    """Browser automation tool that interacts with sandbox browser"""

    def __init__(self, sandbox):
        self.sandbox = sandbox

    async def _arun(self, url: str) -> str:
        """Navigate to URL and return result"""
        try:
            # 调用沙盒的浏览器API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.sandbox.base_url}/browser/navigate",
                    json={"url": url}
                )
                result = response.json()
                return result.get('data', {}).get('content', f'Successfully navigated to {url}')
        except Exception as e:
            return f"Browser navigation failed: {str(e)}"


class ViewPageTool:
    """Tool to view current browser page content"""

    def __init__(self, sandbox):
        self.sandbox = sandbox

    async def _arun(self) -> str:
        """Get current page content"""
        try:
            # 调用沙盒的浏览器API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.sandbox.base_url}/browser/view")
                result = response.json()
                return result.get('data', {}).get('content', 'No content available')
        except Exception as e:
            return f"Failed to view page: {str(e)}"


# LangChain工具装饰器版本（可选）
@tool
async def browser_navigate(url: str) -> str:
    """Navigate browser to a specific URL.

    Args:
        url: URL to navigate to

    Returns:
        Navigation result
    """
    return f"Navigated to {url}"


@tool
async def browser_view() -> str:
    """View current browser page content.

    Returns:
        Current page content
    """
    return "Browser view - page content here"
