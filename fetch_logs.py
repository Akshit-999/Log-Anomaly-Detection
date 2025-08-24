
import time
from typing import Iterator
import os

def tail_file(path: str, poll_interval: float = 0.5) -> Iterator[str]:
    """Yield new lines appended to `path` (like tail -f)."""
    with open(path, "r") as f:
        # go to end
        f.seek(0, os.SEEK_END)   #it's for when new logs are appending to the same file, if you want to read the whole log file from the start,
                                # use f.seek(0)
        while True:
            line = f.readline()
            if line:
                yield line.rstrip("\n")
            else:
                time.sleep(poll_interval)

# Example usage:
# if __name__ == "__main__":
#     for line in tail_file("/Users/akshitagrawal/Desktop/datasets/logproject/synthetic_logs.jsonl"):
#         print(line)
