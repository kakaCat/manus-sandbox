from typing import List, Dict, Any


class Memory:
    def __init__(self):
        self._messages: List[Dict[str, Any]] = []

    def add_message(self, message: Dict[str, Any]):
        self._messages.append(message)

    def add_messages(self, messages: List[Dict[str, Any]]):
        self._messages.extend(messages)

    def get_messages(self) -> List[Dict[str, Any]]:
        return self._messages.copy()

    def get_last_message(self) -> Dict[str, Any] | None:
        if self._messages:
            return self._messages[-1]
        return None

    def roll_back(self):
        if self._messages:
            self._messages.pop()

    def compact(self):
        if len(self._messages) > 10:
            self._messages = self._messages[-10:]

    @property
    def empty(self) -> bool:
        return len(self._messages) == 0
