
from typing import List

DEFAULT_KEYWORDS = ["ERROR", "Exception", "Traceback", "CRITICAL", "Timeout", "FAILED"]

class RulesEngine:
    def __init__(self, keywords=None):
        self.keywords = keywords or DEFAULT_KEYWORDS

    def check(self, raw_log: str) -> bool:
        text = raw_log.lower()
        for kw in self.keywords:
            if kw.lower() in text:
                return True
        return False


