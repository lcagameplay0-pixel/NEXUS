"""Registro de atividades limitado à sessão atual."""

from datetime import datetime


class SessionLog:
    def __init__(self, max_entries=500):
        self.entries = []
        self.max_entries = max_entries

    def add(self, message, level="INFO"):
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "level": level.upper(),
            "message": str(message),
        }

        self.entries.append(entry)

        if len(self.entries) > self.max_entries:
            self.entries.pop(0)

        return entry

    def get_entries(self):
        return list(self.entries)

    def clear(self):
        self.entries.clear()


session_log = SessionLog()
