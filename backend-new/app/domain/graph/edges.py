from typing import Dict, Any


def should_continue(state: Dict[str, Any]) -> str:
    return "end" if state.get("is_complete", False) else "executor"
