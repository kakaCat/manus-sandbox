from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """Search the web for information.

    Args:
        query: Search query

    Returns:
        Search results
    """
    import requests

    try:
        response = requests.get(
            "https://duckduckgo.com/html/",
            params={"q": query},
            timeout=10
        )

        if response.status_code == 200:
            import re
            results = re.findall(r'<a class="result__a" href="([^"]*)"[^>]*>([^<]*)</a>', response.text)

            formatted = []
            for url, title in results[:5]:
                formatted.append(f"- {title.strip()}: {url}")

            return f"Search results for '{query}':\n" + "\n".join(formatted)

        return f"Search error: HTTP {response.status_code}"
    except Exception as e:
        return f"Search error: {str(e)}"
