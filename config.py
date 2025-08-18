"""
config.py
Centralized configuration for LogBERT anomaly detection pipeline.
Values are loaded from environment variables with sensible defaults.
"""

import os
from transformers import AutoTokenizer, AutoModel
AutoTokenizer.from_pretrained("bert-base-uncased")
AutoModel.from_pretrained("bert-base-uncased")

# Model & Inference
LOGBERT_MODEL = os.getenv("LOGBERT_MODEL", "bert-base-uncased")  # Hugging Face Hub model ID

# Windowing
WINDOW_TYPE = os.getenv("WINDOW_TYPE", "count")  # "count", "time", "session"
SEQUENCE_LENGTH = int(os.getenv("SEQUENCE_LENGTH", "20"))     # Only for count-based or event-based
SLIDING_STEP = int(os.getenv("SLIDING_STEP", "5"))            # Only for count-based
TIME_WINDOW_x = int(os.getenv("TIME_WINDOW_SECONDS", "60"))  # Only for time-based

# Anomaly detection
ANOMALY_THRESHOLD = float(os.getenv("ANOMALY_THRESHOLD", "0.85"))  

# Drain3 Log Parser
DRAIN_DEPTH = int(os.getenv("DRAIN_DEPTH", "4"))
DRAIN_SIMILARITY = float(os.getenv("DRAIN_SIMILARITY", "0.5"))

# Alerting
ALERT_MODE = os.getenv("ALERT_MODE", "webhook").lower()  # "webhook" or "fastapi"

# Webhook settings
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK", "")
TEAMS_WEBHOOK = os.getenv("TEAMS_WEBHOOK", "")
EMAIL_SMTP = os.getenv("EMAIL_SMTP", "noreply@logbert.local")

# FastAPI settings
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8000"))

# Alert cooldown to prevent spam
ALERT_COOLDOWN_SECONDS = int(os.getenv("ALERT_COOLDOWN_SECONDS", "60"))

# Explainable AI (optional LLM)
EXPLAINER_MODEL = "gemini-1.5-flash"

# Storage
DB_PATH = os.getenv("DB_PATH", "data/labels.sqlite")

# Misc
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
BATCH_MODE = os.getenv("BATCH_MODE", "false").lower() == "true"  # True = process file instantly
