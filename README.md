# 🚀 LogBERT MVP — Real-Time Log Anomaly Detection  

A production-ready(ish) starter for **real-time log anomaly detection** with:  

- 📡 **Streaming ingestion** (file tail by default; easy hooks for journald/syslog/Kubernetes).  
- 🤖 **Transformer-based anomaly scoring** (BERT-family backbone; pluggable with LogBERT or any HF model).  
- 🔎 **Token-level explanations** via attention + optional LLM explainer (Gemini).  
- ⚖️ **Adaptive thresholding** with feedback stored in SQLite.  
- 📊 **Streamlit dashboard** for live logs, anomalies, scores, and explanations.  

---

## ✨ Key Features
- **Live scoring** of incoming logs with `infer.LogBERTInference`.  
- **Human explanations**: `explainer.explain` converts scores & token importances into plain-English summaries (Gemini optional).  
- **Closed-loop learning**: store human feedback and auto-tune anomaly thresholds (`FeedbackStore.compute_threshold()`).  
- **Pluggable ingestion**: start with `tail -f` on a file; scale to journald/syslog, Kafka, or Kubernetes.  
- **Simple persistence**: SQLite (`feedback.db`) for feedback and thresholds.  

---

## 🗂 Project Layout
```text
├─ app/
│  ├─ dashboard_streamlit.py   # Streamlit UI (live logs & anomalies)
│  └─ replay.py                # Replays timestamped logs
├─ dynamic_log_generator.py    # Fake log generator (writes to dynamic_logs.txt)
├─ fetch_logs.py               # tail_file() + helpers
├─ infer.py                    # LogBERTInference (tokenizer/model, scoring, attentions)
├─ explainer.py                # explain(sequence, score, tokens, token_importance)
├─ store_feedback.py           # SQLite storage + adaptive threshold
├─ config.py                   # Central config & defaults
├─ test_pipeline.py            # Smoke test for the end-to-end loop
├─ requirements.txt            # Python deps
└─ README.md                   # You are here
```

---

## 🔧 Requirements
Python 3.10+
pip / virtualenv (or Conda)
Internet (first run) to download HF model (unless pre-cached)
Optional GPU (CUDA, auto-detected) 
Python dependencies (requirements.txt)
transformers==4.41.1
torch>=2.2,<3
numpy
pandas
streamlit>=1.34
python-dotenv
tqdm 
💡 If using Gemini for LLM explanations, set GOOGLE_API_KEY in your environment. 

---

## ⚙️ Configuration (`config.py`)

All defaults can be overridden via `.env` or environment variables:  

```python
# Model
LOGBERT_MODEL = os.getenv("LOGBERT_MODEL", "bert-base-uncased")

# Windowing
WINDOW_TYPE = os.getenv("WINDOW_TYPE", "count")
SEQUENCE_LENGTH = int(os.getenv("SEQUENCE_LENGTH", "20"))
SLIDING_STEP = int(os.getenv("SLIDING_STEP", "5"))

# Anomaly detection
ANOMALY_THRESHOLD = float(os.getenv("ANOMALY_THRESHOLD", "0.85"))

# Drain3 parser knobs
DRAIN_DEPTH = int(os.getenv("DRAIN_DEPTH", "4"))
DRAIN_SIMILARITY = float(os.getenv("DRAIN_SIMILARITY", "0.5"))

# Explainer model (Gemini)
EXPLAINER_MODEL = "gemini-1.5-flash"

# SQLite DB
DB_PATH = os.getenv("DB_PATH", "<ABSOLUTE_PATH>/feedback.db")

# Logging & modes
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
BATCH_MODE = os.getenv("BATCH_MODE", "false").lower() == "true"
```

## 🚀 Quickstart
1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt

2. (Optional) Pre-download model
python -c "from huggingface_hub import snapshot_download; \
snapshot_download('bert-base-uncased', local_dir='./models/bert-base-uncased')"

export LOGBERT_MODEL=./models/bert-base-uncased
export TRANSFORMERS_OFFLINE=1
export HF_HOME=./.hf_cache

3. Configure .env (optional but recommended)
### .env
LOGBERT_MODEL=./models/bert-base-uncased
DB_PATH=/absolute/path/to/feedback.db
ANOMALY_THRESHOLD=0.85
GOOGLE_API_KEY=your_gemini_key_here   # only if using LLM explanations

4. Generate demo logs
python dynamic_log_generator.py

5. Run dashboard
streamlit run app/dashboard_streamlit.py


## 🧠 Inference & Explainability

infer.LogBERTInference

Loads AutoTokenizer + AutoModelForSequenceClassification.

Uses device_map="auto".

Returns: score, tokens, token_importance, text.

explainer.explain

Input: (sequence, score, tokens, token_importance).

Returns: human-readable rationale.

If GOOGLE_API_KEY set → uses Gemini (gemini-1.5-flash); else template-based explanation.

## 🗄 Feedback & Threshold Adaptation

store_feedback.py manages feedback + thresholds:

feedback(id, timestamp, sequence_text, score, is_true_anomaly)

settings(key PRIMARY KEY, value)

Core methods:

add_feedback(ts, log_text, score, is_true_anomaly)

compute_threshold() → optimizes Youden’s J, saves new threshold

## 📺 Streamlit Dashboard

Live logs (color-coded)

Anomalies table + explanations

Uses fetch_logs.tail_file for ingestion

Can swap with journald, Kafka, K8s, etc.

## 🔌 Ingestion Options

File tail (default)

Journald/syslog (journalctl -f -u <service>)

Kubernetes (kubectl logs -f ...)

Kafka/Fluent Bit/Filebeat → scalable ingestion

Cloud (Cloudwatch, Stackdriver, etc.) → SDK-based

## 🧪 Testing the Pipeline
###Smoke test
```python
python - <<'PY'
from infer import LogBERTInference
m = LogBERTInference()
print(m.infer(["[ERROR] timeout on db retry"]))
PY
```

### CLI scoring
```python
python test_pipeline.py
```

### Dashboard
```python
streamlit run app/dashboard_streamlit.py
```

## 🧱 Production Notes

✅ Fine-tune LogBERT (don’t use plain BERT for prod).

📈 Serve inference via FastAPI/gRPC + Kafka/Redis.

🔍 Add Prometheus metrics.

🗄️ Use Postgres (instead of SQLite).

🔐 Remove PII in logs.

💸 Control costs: fallback to rule-based explanations at high volume.

## 🔮 Roadmap

Fine-tuned LogBERT weights + training scripts.

Postgres storage & labeling UI.

Async/batch inference pipeline.

Alerts → Slack / Teams / Webhooks.

## 📜 License

Choose a license (MIT/Apache 2.0). Place in repo root.



