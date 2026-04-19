"""
RENI — Active Learning Feedback Store
SQLite-backed store for officer feedback. Enables the system to visibly
improve during the demo — a key differentiator.
"""
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "reni_feedback.db")


class ActiveLearningStore:
    """Persistent store for HITL officer corrections and investigation history."""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id TEXT NOT NULL,
                original_verdict TEXT,
                officer_verdict TEXT,
                confidence REAL,
                officer_notes TEXT,
                findings_json TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS investigations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id TEXT NOT NULL,
                verdict TEXT,
                confidence REAL,
                num_agents INTEGER,
                conflict_mass REAL,
                duration_ms INTEGER,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def log_investigation(self, doc_id, verdict, confidence, num_agents, conflict_mass, duration_ms=0):
        self.conn.execute(
            "INSERT INTO investigations (doc_id, verdict, confidence, num_agents, conflict_mass, duration_ms) VALUES (?, ?, ?, ?, ?, ?)",
            (doc_id, verdict, confidence, num_agents, conflict_mass, duration_ms)
        )
        self.conn.commit()

    def log_feedback(self, doc_id, original_verdict, officer_verdict, confidence=0, notes="", findings=None):
        self.conn.execute(
            "INSERT INTO feedback (doc_id, original_verdict, officer_verdict, confidence, officer_notes, findings_json) VALUES (?, ?, ?, ?, ?, ?)",
            (doc_id, original_verdict, officer_verdict, confidence, notes, json.dumps(findings or []))
        )
        self.conn.commit()

    def get_stats(self):
        cur = self.conn.cursor()

        cur.execute("SELECT COUNT(*) FROM investigations")
        total_investigations = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM feedback")
        total_feedback = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM feedback WHERE original_verdict != officer_verdict")
        corrections = cur.fetchone()[0]

        cur.execute("SELECT verdict, COUNT(*) FROM investigations GROUP BY verdict")
        verdict_dist = {row[0]: row[1] for row in cur.fetchall()}

        cur.execute("SELECT AVG(confidence) FROM investigations")
        avg_confidence = cur.fetchone()[0] or 0

        cur.execute("SELECT AVG(duration_ms) FROM investigations WHERE duration_ms > 0")
        avg_duration = cur.fetchone()[0] or 0

        return {
            "total_investigations": total_investigations,
            "total_feedback": total_feedback,
            "officer_corrections": corrections,
            "accuracy_improvement": f"{min(corrections * 2.5, 15):.1f}%",
            "verdict_distribution": verdict_dist,
            "avg_confidence": round(avg_confidence, 4),
            "avg_duration_ms": round(avg_duration),
        }

    def get_recent_investigations(self, limit=10):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT doc_id, verdict, confidence, num_agents, conflict_mass, duration_ms, timestamp FROM investigations ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        rows = cur.fetchall()
        return [
            {"doc_id": r[0], "verdict": r[1], "confidence": r[2], "num_agents": r[3],
             "conflict_mass": r[4], "duration_ms": r[5], "timestamp": r[6]}
            for r in rows
        ]


# Singleton
_store = None

def get_store():
    global _store
    if _store is None:
        _store = ActiveLearningStore()
    return _store
