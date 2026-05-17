import sqlite3
import os
from datetime import datetime
import json
import random

class LeaderboardDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            # Absolute path: always backend/leaderboard.db regardless of CWD
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, '..', 'leaderboard.db')
        self.db_path = os.path.abspath(db_path)
        print(f"[LeaderboardDB] Using database at: {self.db_path}")
        self.init_database()
        self.seed_sample_data()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
        return conn

    def init_database(self):
        """Initialize the database with proper tables"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        with self._get_conn() as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    username TEXT NOT NULL,
                    email TEXT,
                    avatar_url TEXT,
                    joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Leaderboard table — user_id UNIQUE so INSERT OR REPLACE works
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leaderboard (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    points INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    streak INTEGER DEFAULT 0,
                    total_quizzes INTEGER DEFAULT 0,
                    correct_answers INTEGER DEFAULT 0,
                    badges TEXT DEFAULT '[]',
                    weekly_points INTEGER DEFAULT 0,
                    monthly_points INTEGER DEFAULT 0,
                    previous_rank INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # Activity log
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    points_earned INTEGER DEFAULT 0,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            print("✅ LeaderboardDB: tables initialized successfully")

    def seed_sample_data(self):
        """Seed sample leaderboard data only if BOTH tables are empty"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM leaderboard')
            lb_count = cursor.fetchone()[0]
            if lb_count > 0:
                print(f"[LeaderboardDB] Skipping seed — {lb_count} entries already exist")
                return

        print("[LeaderboardDB] Seeding sample data...")
        sample_users = [
            {'user_id': 'demo_1', 'username': 'Alex Johnson',   'email': 'alex@example.com',  'points': 3450, 'streak': 21, 'quizzes': 58, 'correct': 50, 'weekly': 620, 'monthly': 1800, 'badges': '["Quiz Master","Streak Legend","Top Scholar"]', 'prev_rank': 2},
            {'user_id': 'demo_2', 'username': 'Sarah Chen',     'email': 'sarah@example.com', 'points': 2980, 'streak': 14, 'quizzes': 47, 'correct': 41, 'weekly': 480, 'monthly': 1420, 'badges': '["Knowledge Seeker","Quiz Master"]',             'prev_rank': 1},
            {'user_id': 'demo_3', 'username': 'Mike Rodriguez', 'email': 'mike@example.com',  'points': 2640, 'streak': 30, 'quizzes': 53, 'correct': 45, 'weekly': 390, 'monthly': 1150, 'badges': '["Streak Legend","Quiz Master"]',               'prev_rank': 4},
            {'user_id': 'demo_4', 'username': 'Emma Wilson',    'email': 'emma@example.com',  'points': 2210, 'streak': 9,  'quizzes': 39, 'correct': 33, 'weekly': 310, 'monthly': 980,  'badges': '["Knowledge Seeker"]',                         'prev_rank': 3},
            {'user_id': 'demo_5', 'username': 'David Kim',      'email': 'david@example.com', 'points': 1870, 'streak': 17, 'quizzes': 32, 'correct': 27, 'weekly': 240, 'monthly': 760,  'badges': '["Quiz Master"]',                              'prev_rank': 6},
            {'user_id': 'demo_6', 'username': 'Lisa Zhang',     'email': 'lisa@example.com',  'points': 1540, 'streak': 5,  'quizzes': 26, 'correct': 21, 'weekly': 190, 'monthly': 620,  'badges': '["Knowledge Seeker"]',                         'prev_rank': 5},
            {'user_id': 'demo_7', 'username': 'Tom Smith',      'email': 'tom@example.com',   'points': 1230, 'streak': 12, 'quizzes': 22, 'correct': 18, 'weekly': 155, 'monthly': 490,  'badges': '["Quiz Rookie"]',                              'prev_rank': 8},
            {'user_id': 'demo_8', 'username': 'Anna Garcia',    'email': 'anna@example.com',  'points': 980,  'streak': 3,  'quizzes': 18, 'correct': 14, 'weekly': 120, 'monthly': 380,  'badges': '["Quiz Rookie"]',                              'prev_rank': 7},
        ]

        with self._get_conn() as conn:
            cursor = conn.cursor()
            for u in sample_users:
                # Upsert user
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, username, email)
                    VALUES (?, ?, ?)
                ''', (u['user_id'], u['username'], u['email']))

                # Upsert leaderboard entry
                cursor.execute('''
                    INSERT OR REPLACE INTO leaderboard
                        (user_id, points, level, streak, total_quizzes, correct_answers,
                         badges, weekly_points, monthly_points, previous_rank)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    u['user_id'],
                    u['points'],
                    u['points'] // 100 + 1,
                    u['streak'],
                    u['quizzes'],
                    u['correct'],
                    u['badges'],
                    u['weekly'],
                    u['monthly'],
                    u['prev_rank'],
                ))

            conn.commit()

        # Verify
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM leaderboard')
            count = cursor.fetchone()[0]
            print(f"✅ LeaderboardDB: seeded {count} entries successfully")

    def add_user(self, user_id, username, email=None, avatar_url=None):
        """Add or update a user in the system"""
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                # Upsert user (update username/email if already exists)
                cursor.execute('''
                    INSERT INTO users (user_id, username, email, avatar_url, last_active)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id) DO UPDATE SET
                        username = excluded.username,
                        email = COALESCE(excluded.email, email),
                        last_active = CURRENT_TIMESTAMP
                ''', (user_id, username, email, avatar_url))

                # Ensure leaderboard entry exists
                cursor.execute('''
                    INSERT OR IGNORE INTO leaderboard (user_id)
                    VALUES (?)
                ''', (user_id,))

                conn.commit()
            return True
        except Exception as e:
            print(f"[LeaderboardDB] add_user error: {e}")
            return False

    def update_user_score(self, user_id, points_earned, activity_type="general"):
        """Update user's score and related metrics"""
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()

                # Ensure leaderboard row exists first
                cursor.execute('INSERT OR IGNORE INTO leaderboard (user_id) VALUES (?)', (user_id,))

                cursor.execute('''
                    UPDATE leaderboard
                    SET points = points + ?,
                        weekly_points = weekly_points + ?,
                        monthly_points = monthly_points + ?,
                        level = MAX(1, (points + ?) / 100 + 1),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (points_earned, points_earned, points_earned, points_earned, user_id))

                cursor.execute('''
                    INSERT INTO activity_log (user_id, activity_type, points_earned)
                    VALUES (?, ?, ?)
                ''', (user_id, activity_type, points_earned))

                conn.commit()
            return True
        except Exception as e:
            print(f"[LeaderboardDB] update_user_score error: {e}")
            return False

    def update_quiz_stats(self, user_id, quiz_score, max_score=100):
        """Update quiz-related statistics"""
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT OR IGNORE INTO leaderboard (user_id) VALUES (?)', (user_id,))
                is_correct = 1 if quiz_score >= (max_score * 0.8) else 0
                cursor.execute('''
                    UPDATE leaderboard
                    SET total_quizzes = total_quizzes + 1,
                        correct_answers = correct_answers + ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (is_correct, user_id))
                conn.commit()
            return True
        except Exception as e:
            print(f"[LeaderboardDB] update_quiz_stats error: {e}")
            return False

    def get_leaderboard(self, limit=50, time_filter='all', category='points'):
        """Get leaderboard data"""
        sort_column = {
            'points': 'l.points',
            'weekly': 'l.weekly_points',
            'monthly': 'l.monthly_points',
            'quizzes': 'l.total_quizzes',
            'streak': 'l.streak'
        }.get(category, 'l.points')

        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                query = f'''
                    SELECT
                        u.user_id,
                        u.username,
                        u.email,
                        u.avatar_url,
                        u.joined_date,
                        l.points,
                        l.level,
                        l.streak,
                        l.total_quizzes,
                        l.correct_answers,
                        l.badges,
                        l.weekly_points,
                        l.monthly_points,
                        l.previous_rank,
                        CASE
                            WHEN l.total_quizzes > 0
                            THEN ROUND((l.correct_answers * 100.0) / l.total_quizzes, 1)
                            ELSE 0
                        END as average_score
                    FROM users u
                    JOIN leaderboard l ON u.user_id = l.user_id
                    ORDER BY {sort_column} DESC
                    LIMIT ?
                '''
                cursor.execute(query, (limit,))
                results = cursor.fetchall()

                leaderboard = []
                for rank, row in enumerate(results, 1):
                    user_data = dict(row)
                    user_data['rank'] = rank
                    try:
                        user_data['badges'] = json.loads(user_data['badges'] or '[]')
                    except Exception:
                        user_data['badges'] = []
                    leaderboard.append(user_data)

                return leaderboard
        except Exception as e:
            print(f"[LeaderboardDB] get_leaderboard error: {e}")
            return []

    def get_user_rank(self, user_id, category='points'):
        """Get specific user's rank"""
        sort_column = {
            'points': 'points',
            'weekly': 'weekly_points',
            'monthly': 'monthly_points',
            'quizzes': 'total_quizzes',
            'streak': 'streak'
        }.get(category, 'points')

        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    SELECT *,
                        (SELECT COUNT(*) + 1 FROM leaderboard l2
                         WHERE l2.{sort_column} > l1.{sort_column}) as current_rank,
                        CASE
                            WHEN total_quizzes > 0
                            THEN ROUND((correct_answers * 100.0) / total_quizzes, 1)
                            ELSE 0
                        END as average_score
                    FROM leaderboard l1
                    WHERE user_id = ?
                ''', (user_id,))
                result = cursor.fetchone()
                if result:
                    user_data = dict(result)
                    try:
                        user_data['badges'] = json.loads(user_data['badges'] or '[]')
                    except Exception:
                        user_data['badges'] = []
                    return user_data
            return None
        except Exception as e:
            print(f"[LeaderboardDB] get_user_rank error: {e}")
            return None

    def get_leaderboard_stats(self):
        """Get general leaderboard statistics"""
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT
                        COUNT(*) as total_users,
                        AVG(l.points) as avg_points,
                        MAX(l.streak) as max_streak,
                        (SELECT u2.username FROM users u2
                         JOIN leaderboard l2 ON u2.user_id = l2.user_id
                         ORDER BY l2.streak DESC LIMIT 1) as top_streak_user
                    FROM leaderboard l
                ''')
                result = cursor.fetchone()
                return {
                    'totalUsers': result[0] or 0,
                    'averagePoints': round(result[1] or 0, 1),
                    'maxStreak': result[2] or 0,
                    'topStreakUser': result[3] or 'N/A',
                    'mostActiveDay': 'Monday',
                }
        except Exception as e:
            print(f"[LeaderboardDB] get_leaderboard_stats error: {e}")
            return {'totalUsers': 0, 'averagePoints': 0, 'maxStreak': 0, 'topStreakUser': 'N/A', 'mostActiveDay': 'Monday'}


if __name__ == "__main__":
    db = LeaderboardDatabase()
    print("Leaderboard:", db.get_leaderboard(limit=3))
    print("Stats:", db.get_leaderboard_stats())
