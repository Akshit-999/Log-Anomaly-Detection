import sqlite3
from config import DB_PATH, ANOMALY_THRESHOLD

class FeedbackStore:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init()

    def _init(self):
        cur = self.conn.cursor()
        # Feedback table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            sequence_text TEXT,
            score REAL,
            is_true_anomaly INTEGER
        )
        """)
        # Settings table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value REAL
        )
        """)
        self.conn.commit()

    def add_feedback(self, ts, log_text, score, is_true_anomaly: bool):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO feedback (timestamp, sequence_text, score, is_true_anomaly) VALUES (?, ?, ?, ?)",
            (ts, log_text, float(score), int(bool(is_true_anomaly)))
        )
        self.conn.commit()

    def save_threshold(self, value: float):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            ("anomaly_threshold", value)
        )
        self.conn.commit()

    def load_threshold(self, default: float):
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM settings WHERE key=?", ("anomaly_threshold",))
        row = cur.fetchone()
        return row[0] if row else default

    def compute_threshold(self):
        cur = self.conn.cursor()
        cur.execute("SELECT score, is_true_anomaly FROM feedback")
        rows = cur.fetchall()
        if not rows:
            return ANOMALY_THRESHOLD
        rows.sort()
        best = ANOMALY_THRESHOLD
        best_j = -1.0
        scores = [r[0] for r in rows]
        for cut in set(scores):
            tp = sum(1 for s, l in rows if s >= cut and l == 1)
            fn = sum(1 for s, l in rows if s < cut and l == 1)
            fp = sum(1 for s, l in rows if s >= cut and l == 0)
            tn = sum(1 for s, l in rows if s < cut and l == 0)
            tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
            j = tpr - fpr
            if j > best_j:
                best_j = j
                best = cut
        print(f"Computed anomaly threshold: {best:.3f} (based on {len(rows)} feedback records)")
        self.save_threshold(best)
        return best
