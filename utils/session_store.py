from collections import OrderedDict, deque

from core.settings import MAX_HISTORY, MAX_SESSIONS


class SessionStore:
    """In-memory chat history per session id: last MAX_HISTORY turns, at most MAX_SESSIONS sessions."""

    def __init__(self, max_history: int = MAX_HISTORY, max_sessions: int = MAX_SESSIONS):
        self.max_history = max_history
        self.max_sessions = max_sessions
        self._sessions: "OrderedDict[str, deque]" = OrderedDict()

    def get(self, session_id: str) -> deque:
        if session_id not in self._sessions:
            self._sessions[session_id] = deque(maxlen=self.max_history)
            if len(self._sessions) > self.max_sessions:
                self._sessions.popitem(last=False)  # drop the oldest session
        self._sessions.move_to_end(session_id)
        return self._sessions[session_id]
