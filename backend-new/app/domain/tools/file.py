from langchain_core.tools import tool


@tool
def file_read(path: str) -> str:
    """Read file content from the sandbox environment.

    Args:
        path: File path to read

    Returns:
        File content or error message
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"File: {path}\n\nContent:\n{content}"
    except FileNotFoundError:
        return f"File not found: {path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def file_write(path: str, content: str) -> str:
    """Write content to a file in the sandbox environment.

    Args:
        path: File path to write
        content: Content to write

    Returns:
        Success or error message
    """
    import os

    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"
