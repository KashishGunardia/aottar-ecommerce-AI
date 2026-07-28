class ConversationMemory:
    """
    Holds the extracted entities (brand, category, budget, feature, etc.)
    for a SINGLE conversation. One instance per session_key.
    """

    def __init__(self):
        self.memory = {}

    def update(self, entities):

        for key, value in entities.items():

            if value is None:
                continue

            if value == "":
                continue

            if value == []:
                continue

            self.memory[key] = value

    def get(self):
        return self.memory

    def clear(self):
        self.memory = {}

    def merge(self, entities):

        merged = self.memory.copy()

        for k, v in entities.items():

            if v not in [None, "", []]:
                merged[k] = v

        return merged


import threading
import time


class SessionMemoryStore:
    """
    Keeps a SEPARATE ConversationMemory per session_key so one visitor's
    brand/category/budget context never leaks into another visitor's chat.

    Before this, ChatService/ShoppingPipeline held a single global
    ConversationMemory instance shared by every user hitting the backend —
    every conversation was mixing everyone else's context together.

    Idle sessions are swept out automatically after `ttl_seconds` so memory
    usage doesn't grow forever on a long-running server.
    """

    def __init__(self, ttl_seconds: int = 45 * 60):
        self.ttl_seconds = ttl_seconds
        self._sessions = {}  # session_key -> {"memory": ConversationMemory, "last_active": float}
        self._lock = threading.Lock()

    def _sweep_expired(self):
        now = time.time()
        expired_keys = [
            key
            for key, session in self._sessions.items()
            if now - session["last_active"] > self.ttl_seconds
        ]
        for key in expired_keys:
            del self._sessions[key]

    def get_memory(self, session_key: str) -> "ConversationMemory":
        with self._lock:
            self._sweep_expired()

            session = self._sessions.get(session_key)

            if session is None:
                session = {
                    "memory": ConversationMemory(),
                    "last_active": time.time(),
                }
                self._sessions[session_key] = session
            else:
                session["last_active"] = time.time()

            return session["memory"]

    def clear(self, session_key: str):
        with self._lock:
            self._sessions.pop(session_key, None)

    def active_session_count(self) -> int:
        with self._lock:
            self._sweep_expired()
            return len(self._sessions)