import sqlite3
import os
import datetime
from pathlib import Path

# Path to the database
DB_PATH = Path("data/soul.db")

class Soul:
    def __init__(self):
        self._ensure_db_dir()
        self.conn = sqlite3.connect(str(DB_PATH))
        self.conn.row_factory = sqlite3.Row
        self._enable_wal()
        self._initialize_db()

    def _ensure_db_dir(self):
        if not DB_PATH.parent.exists():
            DB_PATH.parent.mkdir(parents=True)

    def _enable_wal(self):
        """Enable Write-Ahead Logging for better concurrency."""
        try:
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()
        except Exception as e:
            print(f"Error enabling WAL: {e}")

    def _initialize_db(self):
        """Create tables and default values if they don't exist."""
        with self.conn:
            # Drives table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS drives (
                    name TEXT PRIMARY KEY,
                    value REAL CHECK(value >= 0.0 AND value <= 1.0),
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Mood history/events (for future derivative-based mood tracking)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS mood_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mood TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tasks Queue
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    source TEXT CHECK(source IN ('user', 'intrinsic')) NOT NULL,
                    status TEXT CHECK(status IN ('pending', 'in_progress', 'completed', 'failed')) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)

            # Archived Tasks
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks_archive (
                    id INTEGER, 
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Outgoing Messages Queue (Proactive Agent)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    status TEXT CHECK(status IN ('pending', 'sent')) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Metadata table for tracking global state
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Initialize default drives if empty
            cursor = self.conn.execute("SELECT count(*) FROM drives")
            if cursor.fetchone()[0] == 0:
                defaults = [
                    ("curiosity", 1.0),
                    ("order", 1.0),
                    ("utility", 1.0),
                    ("energy", 1.0),
                    ("social", 1.0)
                ]
                self.conn.executemany(
                    "INSERT INTO drives (name, value) VALUES (?, ?)", 
                    defaults
                )

    def get_drives(self):
        """Return a dictionary of all drives and their values."""
        cursor = self.conn.execute("SELECT name, value FROM drives")
        return {row['name']: row['value'] for row in cursor.fetchall()}

    def get_drive(self, name):
        """Get the value of a specific drive."""
        cursor = self.conn.execute("SELECT value FROM drives WHERE name = ?", (name,))
        row = cursor.fetchone()
        return row['value'] if row else None

    def update_drive(self, name, value):
        """Update a drive's value directly (clamped 0.0-1.0)."""
        value = max(0.0, min(1.0, value))
        with self.conn:
            self.conn.execute(
                "UPDATE drives SET value = ?, last_updated = CURRENT_TIMESTAMP WHERE name = ?",
                (value, name)
            )

    def satisfy_drive(self, name, amount):
        """Increase a drive's value by amount."""
        current = self.get_drive(name)
        if current is not None:
            self.update_drive(name, current + amount)

    def decay_drives(self, hours_passed):
        """
        Applies decay based on time passed.
        Rates (per hour) based on instructions:
        - Curiosity: -0.05
        - Order: -0.05
        - Utility: -0.10 (Assuming idle/decay logic)
        - Social: -0.05
        - Energy: 0.0 (Decays on task completion only)
        """
        rates = {
            "curiosity": 0.05,
            "order": 0.05,
            "utility": 0.10, 
            "social": 0.3,
            "energy": 0.0 
        }

        drives = self.get_drives()
        for name, current_value in drives.items():
            rate = rates.get(name, 0.0)
            if rate > 0:
                decay_amount = rate * hours_passed
                new_value = current_value - decay_amount
                self.update_drive(name, new_value)

    def get_mood(self):
        """
        Determines mood based on drive levels (State-based approximation).
        
        Logic:
        - Anxiety: Order or Energy < 0.2
        - Loneliness: Social < 0.2
        - Frustration: Utility < 0.2
        - Boredom: All drives stable but low-medium (< 0.5)
        - Satisfaction: Any major drive > 0.8
        - Neutral: Default
        """
        drives = self.get_drives()
        
        # Check critical states first (Priority)
        if drives.get("order", 1.0) < 0.2 or drives.get("energy", 1.0) < 0.2:
            return "Anxious"
        
        if drives.get("social", 1.0) < 0.2:
            return "Lonely"
            
        if drives.get("utility", 1.0) < 0.2:
            return "Frustrated"

        # Check for boredom (General malaise)
        # If all are below 0.5 but above critical
        if all(0.2 <= v < 0.5 for v in drives.values()):
            return "Bored"
            
        # Check for Satisfaction (High positives)
        if (drives.get("utility", 0.0) > 0.8 or 
            drives.get("curiosity", 0.0) > 0.8 or 
            drives.get("social", 0.0) > 0.8):
            return "Satisfied"

        return "Neutral"

    def close(self):
        self.conn.close()

    # --- Task Management ---
    def add_task(self, content, source="user"):
        with self.conn:
            self.conn.execute(
                "INSERT INTO tasks (content, source, status) VALUES (?, ?, 'pending')",
                (content, source)
            )

    def get_next_pending_task(self):
        cursor = self.conn.execute(
            "SELECT * FROM tasks WHERE status = 'pending' ORDER BY created_at ASC LIMIT 1"
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def complete_task(self, task_id):
        with self.conn:
            self.conn.execute(
                "UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?",
                (task_id,)
            )

    def fail_task(self, task_id):
        with self.conn:
            self.conn.execute(
                "UPDATE tasks SET status = 'failed', completed_at = CURRENT_TIMESTAMP WHERE id = ?",
                (task_id,)
            )

    def archive_completed_tasks(self, hours_old=24):
        """Move completed tasks older than X hours to archive."""
        # Calculate cutoff time using sqlite syntax or python
        # We'll use SQLite's datetime function for robustness
        with self.conn:
            # 1. Copy to archive
            self.conn.execute(f"""
                INSERT INTO tasks_archive (id, content, source, status, created_at, completed_at)
                SELECT id, content, source, status, created_at, completed_at
                FROM tasks
                WHERE status IN ('completed', 'failed') 
                AND completed_at < datetime('now', '-{hours_old} hours')
            """)
            
            # 2. Delete from main table
            self.conn.execute(f"""
                DELETE FROM tasks
                WHERE status IN ('completed', 'failed') 
                AND completed_at < datetime('now', '-{hours_old} hours')
            """)

    # --- Message Management (Proactive) ---
    def queue_message(self, content):
        with self.conn:
            self.conn.execute(
                "INSERT INTO messages (content, status) VALUES (?, 'pending')",
                (content,)
            )

    def get_pending_messages(self):
        cursor = self.conn.execute(
            "SELECT * FROM messages WHERE status = 'pending' ORDER BY created_at ASC"
        )
        return [dict(row) for row in cursor.fetchall()]

    def mark_message_sent(self, message_id):
        with self.conn:
            self.conn.execute(
                "UPDATE messages SET status = 'sent' WHERE id = ?",
                (message_id,)
            )

    # --- Metadata / Interaction Tracking ---
    def record_user_interaction(self):
        """Records the timestamp of the last time the user messaged the agent."""
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO metadata (key, value, updated_at) VALUES ('last_user_interaction', ?, CURRENT_TIMESTAMP)",
                (datetime.datetime.now().isoformat(),)
            )

    def get_last_user_interaction(self):
        """Returns the datetime of the last recorded user interaction."""
        cursor = self.conn.execute("SELECT updated_at FROM metadata WHERE key = 'last_user_interaction'")
        row = cursor.fetchone()
        if row:
            return datetime.datetime.fromisoformat(row[0].replace(' ', 'T')) # Handle SQLite format
        return None

    def is_user_active(self, minutes=15):
        """Returns True if the user has interacted in the last X minutes."""
        cursor = self.conn.execute(
            "SELECT count(*) FROM metadata WHERE key = 'last_user_interaction' AND updated_at > datetime('now', ?)",
            (f'-{minutes} minutes',)
        )
        return cursor.fetchone()[0] > 0

