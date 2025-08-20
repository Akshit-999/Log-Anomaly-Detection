import streamlit as st
import time
import pandas as pd
from explainer import explain
from store_feedback import FeedbackStore
from infer import LogBERTInference
from fetch_logs import tail_file

# --- Init ---
st.set_page_config(page_title="🚨 Log Anomaly Dashboard", layout="wide")
st.title("🚨 Real-Time Log Anomaly Dashboard")
st.caption("Monitor logs, detect anomalies, and view remedies in real-time.")

logbert = LogBERTInference()
feedback_store = FeedbackStore("feedback.db")
log_path = "/teamspace/studios/this_studio/dynamic_logs.txt"

# --- Session State ---
if "logs" not in st.session_state:
    st.session_state.logs = []
if "anomalies" not in st.session_state:
    st.session_state.anomalies = []
if "total_logs" not in st.session_state:
    st.session_state.total_logs = 0

# --- Top Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Logs", st.session_state.total_logs)
col2.metric("Anomalies", len(st.session_state.anomalies))
col3.metric("Threshold", f"{feedback_store.compute_threshold():.2f}")

# --- Layout ---
left, right = st.columns([2, 3])

# --- Live Logs ---
with left:
    st.subheader("📜 Live Logs (last 20)")
    logs_display = ""
    for log in st.session_state.logs:
        if "CRITICAL" in log or "ERROR" in log:
            logs_display += f"<span style='color:red;'>{log}</span><br>"
        elif "WARN" in log:
            logs_display += f"<span style='color:orange;'>{log}</span><br>"
        else:
            logs_display += f"<span style='color:gray;'>{log}</span><br>"
    st.markdown(logs_display, unsafe_allow_html=True)

# --- Anomalies ---
with right:
    st.subheader("🚩 Anomalous Logs")
    if st.session_state.anomalies:
        df = pd.DataFrame(st.session_state.anomalies)
        st.dataframe(df, use_container_width=True)
    else:
        st.success("✅ No anomalies detected.")

# --- Stream new logs ---
for line in tail_file(log_path, poll_interval=1):
    ts = int(time.time())
    result = logbert.infer([line])
    score = result["score"]

    # Store feedback
    feedback_store.add_feedback(ts, line, score, None)
    threshold = feedback_store.compute_threshold()

    # Update stats
    st.session_state.total_logs += 1
    st.session_state.logs.append(f"{line} | score={score:.3f}")
    st.session_state.logs = st.session_state.logs[-20:]

    # Anomaly handling
    if score > threshold:
        explanation = explain(
            sequence=[line],
            score=score,
            tokens=result["tokens"],
            token_importance=result["token_importance"]
        )

        st.session_state.anomalies.append({
            "ts": ts,
            "log": line,
            "score": score,
            "explanation": explanation,
        })
        st.session_state.anomalies = st.session_state.anomalies[-50:]

    st.rerun()
