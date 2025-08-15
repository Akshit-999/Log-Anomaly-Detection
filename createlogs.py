import pandas as pd
import random
import uuid
from datetime import datetime, timedelta

# Parameters
num_logs = 100000
anomaly_ratio = 0.05  
log_templates = [
    "GET /index.html 200",
    "POST /login 200",
    "GET /dashboard 200",
    "GET /nonexistentpage 404",
    "POST /login 401",
    "GET /api/data 500",
    "User login successful",
    "User login failed",
    "Database connection error",
    "File not found exception",
    "User logout successful",
    "Payment processing failed",
    "Session timeout error",
    "CPU usage high",
    "Memory leak detected",
    "Connection timeout after %d ms",
    "Request failed with status %d",
    "Memory usage at %d%%",
    "Thread pool exhausted (%d active)",
    "Rate limit exceeded: %d requests/sec"
]

# Add pattern variations
def generate_log_message(template):
    if "%d" in template:
        return template % random.randint(1, 1000)
    return template

# Tag some templates as anomalies
anomalous_templates = {"POST /login 401", "GET /api/data 500", "Database connection error",
                      "File not found exception", "Payment processing failed",
                      "Memory leak detected", "CPU usage high"}

severity_levels = ['INFO', 'WARN', 'ERROR', 'CRITICAL']

# Generate log entries
start_time = datetime(2025, 1, 1)
logs = []
for i in range(num_logs):
    timestamp = start_time + timedelta(seconds=random.randint(0, 1000000))
    template = random.choice(log_templates)
    log_id = str(uuid.uuid4())
    severity = random.choice(severity_levels)
    message = f"[{severity}] {generate_log_message(template)}"
    label = 1 if template in anomalous_templates and random.random() < anomaly_ratio else 0
    logs.append({"timestamp": timestamp.isoformat(), "log_id": log_id, "log": message, "anomaly": label})

# Create DataFrame and save
log_df = pd.DataFrame(logs)
csv_path = "/Users/akshitagrawal/Desktop/datasets/logproject/synthetic_logs.csv"
jsonl_path = "/Users/akshitagrawal/Desktop/datasets/logproject/synthetic_logs.jsonl"
log_df.to_csv(csv_path, index=False)
log_df.to_json(jsonl_path, orient="records", lines=True)
