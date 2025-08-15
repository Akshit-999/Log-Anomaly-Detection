
from datetime import datetime, timedelta
from collections import deque, defaultdict
from drain3.file_persistence import FilePersistence
import json
import config 
import re
from fetch_logs import tail_file


class SequenceWindow:
    def __init__(self):
        self.buffer = deque()
        self.timestamps = deque()
        self.sessions = defaultdict(deque)

    def add_log(self, log_line):
        now = datetime.now()

        if config.WINDOW_TYPE == "count":
            self.buffer.append(log_line)
            if len(self.buffer) > config.SEQUENCE_LENGTH:
                for _ in range(config.SLIDING_STEP):
                    if self.buffer:
                        self.buffer.popleft()

            if len(self.buffer) == config.SEQUENCE_LENGTH:
                return list(self.buffer)

        elif config.WINDOW_TYPE == "time":
            self.buffer.append(log_line)
            self.timestamps.append(now)
            while self.timestamps and (now - self.timestamps[0]).total_seconds() > config.TIME_WINDOW_SECONDS:
                self.buffer.popleft()
                self.timestamps.popleft()

            if len(self.buffer) >= config.SEQUENCE_LENGTH:
                return list(self.buffer)

        elif config.WINDOW_TYPE == "session":
            session_id = self.extract_session_id(log_line)
            self.sessions[session_id].append(log_line)
            self.buffer = self.sessions[session_id]

            if len(self.buffer) >= config.SEQUENCE_LENGTH:
                return list(self.buffer)

        return None


    def get_sequence(self):
        return list(self.buffer)


    @staticmethod
    def extract_session_id(log_line):
        # If the log line is already parsed as a dictionary (e.g., from JSONL)
        if isinstance(log_line, dict):
            return log_line.get("session_id", "unknown")

        # If it's a string starting with '{', try parsing as JSON
        if isinstance(log_line, str) and log_line.strip().startswith("{"):
            try:
                log_obj = json.loads(log_line)
                return log_obj.get("session_id", "unknown")
            except json.JSONDecodeError:
                pass  # Fall through to regex check

        # If none of the above, use regex to search for "session=<id>"
        match = re.search(r"session[_=]([A-Za-z0-9_-]+)", log_line)
        return match.group(1) if match else "unknown"

        

if __name__ == "__main__":
    window = SequenceWindow()

    log_path = "/Users/akshitagrawal/Desktop/datasets/logproject/synthetic_logs.jsonl"
    for line in tail_file(log_path):
        try:
            log_dict = json.loads(line)
            log_msg = log_dict.get("log", line)  
        except json.JSONDecodeError:
            log_msg = line  
        s = window.add_log(log_msg)

        print(window.get_sequence())
