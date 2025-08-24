from explainer import explain
from store_feedback import FeedbackStore
from infer import LogBERTInference
from fetch_logs import tail_file
import time
import itertools
import time

logbert = LogBERTInference()
log_path = "dynamic_logs.txt"
feedback_store = FeedbackStore("feedback.db")

for line in itertools.islice(tail_file(log_path, poll_interval=1), 20):
    ts = int(time.time())  # current timestamp

    # wrap single log line as a "sequence"
    result = logbert.infer([line])

    print("Anomaly Score:", result["score"])
    print("Text Processed:", result["text"])

    # only explain if anomaly score is high
    if result["score"] > 0.1:
        explanation = explain(
            sequence=[line],  # keep same format you used in training
            score=result["score"],
            tokens=result["tokens"],
            token_importance=result["token_importance"]
        )
        print("🚨 LLM Explanation:", explanation)

    print("---")

    # Store feedback in DB
    feedback_store.add_feedback(
        ts=ts,
        log_text=line,               # actual log line
        score=result["score"],       # anomaly score
        is_true_anomaly=None         # placeholder, update later
    )
    feedback_store.compute_threshold()



# import sqlite3
# from pprint import pprint

# conn = sqlite3.connect("feedback.db")
# cur = conn.cursor()

# cur.execute("SELECT * FROM settings LIMIT 5")
# rows = cur.fetchall()

# for row in rows:
#     # print("\n--- Feedback Record ---")
#     # print(f"ID: {row[0]}")
#     # print(f"Log: {row[2]}")
#     # print(f"Score: {row[3]}")
#     # print(f"Label: {row[4]}")
#     # print("Explanation:")
#     # print(row[1])

#     print("\n--- Feedback Record ---")
#     print(f"key: {row[0]}")
#     print(f"value: {row[1]}")

