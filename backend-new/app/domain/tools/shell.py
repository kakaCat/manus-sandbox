from langchain_core.tools import BaseTool, tool


class ShellExecuteInput:
    command: str

    def __init__(self, command: str):
        self.command = command


@tool
def shell_execute(command: str) -> str:
    """Execute a shell command in the sandbox environment.

    Args:
        command: Shell command to execute

    Returns:
        Command output or error message
    """
    import subprocess
    import shlex

    try:
        result = subprocess.run(
            shlex.split(command),
            capture_output=True,
            text=True,
            timeout=60
        )
        output = result.stdout or result.stderr
        return f"Command: {command}\nOutput: {output}"
    except subprocess.TimeoutExpired:
        return f"Command timed out: {command}"
    except Exception as e:
        return f"Error executing command: {str(e)}"
