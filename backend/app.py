import os
import json
import requests
from dotenv import load_dotenv
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from werkzeug.utils import secure_filename
import kokoro
from kokoro import KPipeline
import soundfile as sf
import numpy as np
import re
import pdfplumber
import torch
import io
from typing import List
from agents import AgentService, SafetyStatus
import time
from datetime import datetime, timedelta
from openai import OpenAI
import whisper
from models.gamification import GamificationDB
from services.points_service import PointsService
import sqlite3
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, JSON, Boolean, func
from sqlalchemy.orm import declarative_base, sessionmaker
import json
import os
from database.leaderboard_db import LeaderboardDatabase
import warnings
warnings.filterwarnings("ignore", ".*declarative_base.*")

from dotenv import load_dotenv
load_dotenv()

# Single Flask app instance (previously duplicated causing CORS issues)
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Permissive CORS for local development — allows all localhost ports & methods (including OPTIONS preflight)
CORS(app,
     origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     supports_credentials=True)

print("✅ Flask app and CORS initialized successfully!")

github_token = os.getenv("GITHUB_TOKEN")

client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=github_token,
) if github_token else None
leaderboard_db = LeaderboardDatabase()

Base = declarative_base()

class LeaderboardEntry(Base):
    __tablename__ = 'leaderboard_v2'  # Changed table name to avoid conflicts
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), unique=True, nullable=False)
    user_name = Column(String(100), nullable=False)
    user_email = Column(String(100), nullable=True)
    points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak = Column(Integer, default=0)
    total_quizzes = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    badges = Column(String(1000), default='[]')  # Store as JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    weekly_points = Column(Integer, default=0)
    monthly_points = Column(Integer, default=0)
    previous_rank = Column(Integer, default=0)

# 5. CREATE DATABASE ENGINE (lines 101-120)
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'leaderboard_v2.db')
engine = create_engine(f'sqlite:///{DATABASE_PATH}')

# ✅ Then use engine to create tables
try:
    Base.metadata.drop_all(engine)  # Remove old conflicting tables
    Base.metadata.create_all(engine)  # Create new tables with correct schema
    print("✅ Database schema updated successfully!")
except Exception as e:
    print(f"❌ Database creation error: {str(e)}")

# ✅ Create session factory
Session = sessionmaker(bind=engine)

def create_sample_data():
    """Create sample data if database is empty"""
    session = Session()
    
    try:
        # Check if data exists
        if session.query(LeaderboardEntry).count() == 0:
            print("📊 Creating sample leaderboard data...")
            
            sample_users = [
                {
                    'user_id': 'sample_user_1',
                    'user_name': 'Alex Johnson',
                    'points': 2450,
                    'level': 24,
                    'streak': 15,
                    'total_quizzes': 45,
                    'correct_answers': 38,
                    'weekly_points': 450,
                    'monthly_points': 1200,
                    'badges': '["Quiz Master", "Streak Legend"]'
                },
                {
                    'user_id': 'sample_user_2', 
                    'user_name': 'Sarah Chen',
                    'points': 2120,
                    'level': 21,
                    'streak': 8,
                    'total_quizzes': 38,
                    'correct_answers': 32,
                    'weekly_points': 320,
                    'monthly_points': 980,
                    'badges': '["Knowledge Seeker"]'
                },
                {
                    'user_id': 'sample_user_3',
                    'user_name': 'Mike Rodriguez',
                    'points': 1890,
                    'level': 18,
                    'streak': 22,
                    'total_quizzes': 41,
                    'correct_answers': 35,
                    'weekly_points': 280,
                    'monthly_points': 850,
                    'badges': '["Streak Legend", "Quiz Master"]'
                },
                {
                    'user_id': 'sample_user_4',
                    'user_name': 'Emma Wilson',
                    'points': 1650,
                    'level': 16,
                    'streak': 12,
                    'total_quizzes': 33,
                    'correct_answers': 28,
                    'weekly_points': 220,
                    'monthly_points': 720,
                    'badges': '["Knowledge Seeker"]'
                },
                {
                    'user_id': 'sample_user_5',
                    'user_name': 'David Kim',
                    'points': 1420,
                    'level': 14,
                    'streak': 6,
                    'total_quizzes': 29,
                    'correct_answers': 24,
                    'weekly_points': 180,
                    'monthly_points': 600,
                    'badges': '["Quiz Master"]'
                }
            ]
            
            for user_data in sample_users:
                user_entry = LeaderboardEntry(**user_data)
                session.add(user_entry)
            
            session.commit()
            print("✅ Sample leaderboard data created!")
        else:
            print("📊 Leaderboard data already exists")
    
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        session.rollback()
    finally:
        session.close()
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), unique=True, nullable=False)
    user_name = Column(String(100), nullable=False)
    user_email = Column(String(100), nullable=True)
    points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak = Column(Integer, default=0)
    total_quizzes = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    badges = Column(String(1000), default='[]')  # Store as JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    weekly_points = Column(Integer, default=0)
    monthly_points = Column(Integer, default=0)
    previous_rank = Column(Integer, default=0)

# 5. CREATE DATABASE ENGINE (lines 101-120)
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'leaderboard_v2.db')
engine = create_engine(f'sqlite:///{DATABASE_PATH}')

# ✅ Then use engine to create tables
try:
    Base.metadata.drop_all(engine)  # Remove old conflicting tables
    Base.metadata.create_all(engine)  # Create new tables with correct schema
    print("✅ Database schema updated successfully!")
except Exception as e:
    print(f"❌ Database creation error: {str(e)}")

# ✅ Create session factory
Session = sessionmaker(bind=engine)

def create_sample_data():
    """Create sample data if database is empty"""
    session = Session()
    
    try:
        # Check if data exists
        if session.query(LeaderboardEntry).count() == 0:
            print("📊 Creating sample leaderboard data...")
            
            sample_users = [
                {
                    'user_id': 'sample_user_1',
                    'user_name': 'Alex Johnson',
                    'points': 2450,
                    'level': 24,
                    'streak': 15,
                    'total_quizzes': 45,
                    'correct_answers': 38,
                    'weekly_points': 450,
                    'monthly_points': 1200,
                    'badges': '["Quiz Master", "Streak Legend"]'
                },
                {
                    'user_id': 'sample_user_2', 
                    'user_name': 'Sarah Chen',
                    'points': 2120,
                    'level': 21,
                    'streak': 8,
                    'total_quizzes': 38,
                    'correct_answers': 32,
                    'weekly_points': 320,
                    'monthly_points': 980,
                    'badges': '["Knowledge Seeker"]'
                },
                {
                    'user_id': 'sample_user_3',
                    'user_name': 'Mike Rodriguez',
                    'points': 1890,
                    'level': 18,
                    'streak': 22,
                    'total_quizzes': 41,
                    'correct_answers': 35,
                    'weekly_points': 280,
                    'monthly_points': 850,
                    'badges': '["Streak Legend", "Quiz Master"]'
                },
                {
                    'user_id': 'sample_user_4',
                    'user_name': 'Emma Wilson',
                    'points': 1650,
                    'level': 16,
                    'streak': 12,
                    'total_quizzes': 33,
                    'correct_answers': 28,
                    'weekly_points': 220,
                    'monthly_points': 720,
                    'badges': '["Knowledge Seeker"]'
                },
                {
                    'user_id': 'sample_user_5',
                    'user_name': 'David Kim',
                    'points': 1420,
                    'level': 14,
                    'streak': 6,
                    'total_quizzes': 29,
                    'correct_answers': 24,
                    'weekly_points': 180,
                    'monthly_points': 600,
                    'badges': '["Quiz Master"]'
                }
            ]
            
            for user_data in sample_users:
                user_entry = LeaderboardEntry(**user_data)
                session.add(user_entry)
            
            session.commit()
            print("✅ Sample leaderboard data created!")
        else:
            print("📊 Leaderboard data already exists")
    
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        session.rollback()
    finally:
        session.close()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class RateLimitedGeminiAPI:
    def __init__(self, api_key, model="gemini-1.5-pro-latest"):
        self.api_key = api_key
        self.last_request_time = None
        self.min_interval = 1
        self.retry_attempts = 2
        self.base_delay = 0.5
        self.model = model
        
    def call_gemini_api(self, prompt, model_override=None):
        if not self.api_key:
            return None
        if not self.api_key.startswith('AIzaSy'):
            return None
        if self.last_request_time:
            time_since_last = time.time() - self.last_request_time
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                time.sleep(sleep_time)
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model_override or self.model}:generateContent?key={self.api_key}"
        )
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        for attempt in range(self.retry_attempts):
            try:
                self.last_request_time = time.time()
                response = requests.post(url, headers=headers, json=data, timeout=15)
                if response.status_code == 200:
                    return response.json()["candidates"][0]["content"]["parts"][0]["text"]
                elif response.status_code == 429:
                    if attempt < self.retry_attempts - 1:
                        time.sleep(self.base_delay * (2 ** attempt))
                        continue
                    else:
                        return None
                else:
                    response.raise_for_status()
            except Exception:
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.base_delay * (2 ** attempt))
                    continue
                return None
        return None

gemini_api = RateLimitedGeminiAPI(GEMINI_API_KEY, model="gemini-1.5-pro-latest")
gemini_flash_api = RateLimitedGeminiAPI(GEMINI_API_KEY, model="gemini-1.5-flash")

def call_gemini_api(prompt, use_github_api=True, model_override=None):
    if use_github_api and client and github_token:
        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that creates educational content and answers questions. Always include at least one diagram or visual explanation in the output.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="openai/gpt-4o",
                temperature=0.8,
                max_tokens=1800,
                top_p=1
            )
            return response.choices[0].message.content
        except Exception:
            pass
    api = gemini_flash_api if model_override == "flash" else gemini_api
    return api.call_gemini_api(prompt, model_override="gemini-1.5-flash" if model_override == "flash" else None)

def build_prompt_with_heading_and_diagram(title, content, icon="📘"):
    return (
        f"## {icon} {title}\n"
        "Please answer in the following format:\n"
        "- Start with a large, bold markdown heading (##) and a relevant icon for the topic.\n"
        "- Add a diagram (as a Markdown image, ASCII, or a creative visual analogy) and provide a caption. If you can't generate an image, use ASCII or a creative analogy in markdown.\n"
        "- Structure your explanation as concise bullet points (not paragraphs).\n"
        "- Always include the diagram and the points, even if you must invent a visual analogy.\n\n"
        f"Content to answer: {content}\n"
    )

def process_with_gemini(text, use_github_api=True):
    summary_title = "AI Answer"
    prompt = build_prompt_with_heading_and_diagram(summary_title, text, "📘")
    result = call_gemini_api(prompt, use_github_api=use_github_api, model_override="flash")
    if result is None:
        return gemini_flash_api.call_gemini_api(prompt, model_override="gemini-1.5-flash")
    return result

chat_history = []
vector_store = None
agent_service = AgentService(api_key=GEMINI_API_KEY)


# Initialize gamification database
def init_gamification_db():
    """Initialize the gamification database - this creates the .db file automatically"""
    db_path = os.path.join(os.path.dirname(__file__), 'gamification.db')
    
    print(f"🗄️ Creating database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            total_points INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            streak_days INTEGER DEFAULT 0,
            last_active DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Point transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS point_transactions (
            transaction_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            points_earned INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            description TEXT,
            metadata TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Badges table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS badges (
            badge_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            icon_url TEXT,
            points_required INTEGER DEFAULT 0,
            category TEXT DEFAULT 'achievement',
            unlock_condition TEXT
        )
    ''')
    
    # User badges table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_badges (
            user_id TEXT NOT NULL,
            badge_id TEXT NOT NULL,
            earned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            progress_percentage INTEGER DEFAULT 100,
            PRIMARY KEY (user_id, badge_id),
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (badge_id) REFERENCES badges (badge_id)
        )
    ''')
    
    # Seed initial badges
    badges = [
        ("first_quiz", "Quiz Rookie", "Complete your first quiz", "🎯", 0, "achievement"),
        ("quiz_master", "Quiz Master", "Complete 10 quizzes", "🏆", 150, "achievement"),
        ("streak_7", "Week Warrior", "7-day learning streak", "🔥", 100, "streak"),
        ("points_100", "Century Club", "Earn 100 points", "💯", 100, "points"),
        ("points_500", "High Achiever", "Earn 500 points", "⭐", 500, "points"),
        ("perfect_quiz", "Perfectionist", "Score 100% on a quiz", "🎯", 50, "achievement"),
        ("social_learner", "Helper", "Help 5 peers", "🤝", 75, "social"),
        ("content_creator", "Content Creator", "Upload 5 learning materials", "📚", 100, "social"),
    ]
    
    for badge in badges:
        cursor.execute('''
            INSERT OR IGNORE INTO badges 
            (badge_id, name, description, icon_url, points_required, category)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', badge)
    
    conn.commit()
    conn.close()
    
    print("✅ Gamification database initialized successfully!")
    return db_path
def get_db_path():
    """Get the database path"""
    return os.path.join(os.path.dirname(__file__), 'gamification.db')

# Points calculation functions
def calculate_quiz_points(quiz_score):
    """Calculate points based on quiz performance"""
    if quiz_score >= 1.0:  # 100%
        return 25, "perfect_quiz"
    elif quiz_score >= 0.8:  # 80%+
        return 20, "quiz_completed"
    elif quiz_score >= 0.6:  # 60%+
        return 15, "quiz_completed"
    else:
        return 10, "quiz_completed"

def award_points(user_id, points, activity_type, description):
    """Award points to user and update their total"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    transaction_id = str(uuid.uuid4())
    
    # Add points transaction
    cursor.execute('''
        INSERT INTO point_transactions 
        (transaction_id, user_id, points_earned, activity_type, description, timestamp)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (transaction_id, user_id, points, activity_type, description))
    
    # Update or create user record
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, email, total_points, level)
        VALUES (?, 'Anonymous', 'unknown@example.com', 0, 1)
    ''', (user_id,))
    
    # Update user total points and level
    cursor.execute('''
        UPDATE users 
        SET total_points = total_points + ?,
            level = (total_points + ?) / 100 + 1,
            last_active = CURRENT_TIMESTAMP
        WHERE user_id = ?
    ''', (points, points, user_id))
    
    conn.commit()
    conn.close()
    
    return transaction_id

# INITIALIZE THE DATABASE WHEN THE APP STARTS
print("🚀 Initializing Tayyari.ai backend...")
init_gamification_db()

DOWNLOADS_DIR = "downloads"
UPLOAD_FOLDER = "uploads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def download_file(file_url):
    try:
        if file_url.endswith('.pdf'):
            filename = file_url.split("/")[-1]
        else:
            filename = file_url.split("/")[-2] + ".pdf"
        local_filename = os.path.join(DOWNLOADS_DIR, filename)
        response = requests.get(file_url, stream=True, timeout=30)
        response.raise_for_status()
        with open(local_filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return local_filename
    except requests.exceptions.RequestException:
        return None
    except Exception:
        return None

def extract_text_from_pdf(pdf_path):
    try:
        try:
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            text = "\n".join([page.page_content for page in pages if page.page_content])
            if text.strip():
                return text
        except Exception:
            pass
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                if text_parts:
                    text = "\n".join(text_parts)
                    text = re.sub(r"(\w+)\s*\n\s*(\w+)", r"\1 \2", text)
                    return text
        except Exception:
            pass
        return ""
    except Exception:
        return ""

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                'fileUrl': f'/uploads/{filename}'
            }), 200
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def split_text_for_rag(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return text_splitter.split_text(text)

@app.route('/test-github-api', methods=['POST'])
def test_github_api():
    try:
        data = request.json
        prompt = data.get('prompt', 'What is the capital of France?')
        if not client:
            return jsonify({
                'error': 'GitHub API not configured. Please set GITHUB_TOKEN environment variable.'
            }), 400
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant.",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="openai/gpt-4o",
            temperature=1,
            max_tokens=4096,
            top_p=1
        )
        return jsonify({
            'response': response.choices[0].message.content,
            'status': 'success',
            'api_used': 'github_openai'
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/process-interaction', methods=['POST'])
def process_interaction():
    try:
        data = request.json
        user_input = data.get('input')
        if not user_input:
            return jsonify({
                'error': 'No input provided'
            }), 400
        current_topic = data.get('current_topic')
        active_subtopic = data.get('active_subtopic')
        session_history = data.get('session_history')
        response = agent_service.start_new_topic(user_input, current_topic=current_topic, active_subtopic=active_subtopic, session_history=session_history)
        response_dict = response.to_dict()
        return jsonify(response_dict)
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

def generate_audio(text):
    generator = pipeline(
        text, voice='af_heart',
        speed=1
    )
    all_audio = []
    for i, (gs, ps, audio) in enumerate(generator):
        all_audio.append(audio)
    final_audio = np.concatenate(all_audio)
    return final_audio

@app.route("/process-text2speech", methods=["POST"])
def process_text2speech():
    text = ""
    if "pdf" in request.files:
        file = request.files["pdf"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        try:
            with pdfplumber.open(file_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                text = " ".join(text_parts)
            text = re.sub(r"(\w+)\s*\n\s*(\w+)", r"\1 \2", text)
            try:
                os.remove(file_path)
            except Exception:
                pass
        except Exception as e:
            try:
                os.remove(file_path)
            except:
                pass
            return jsonify({"error": f"Could not extract text from PDF: {str(e)}"}), 400
    else:
        text = request.form.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
    try:
        audio = generate_audio(text)
        wav_file = io.BytesIO()
        sf.write(wav_file, audio, 24000, format='WAV')
        wav_file.seek(0)
        return send_file(wav_file, mimetype='audio/wav', as_attachment=False)
    except Exception as e:
        return jsonify({"error": f"Could not generate audio: {str(e)}"}), 500

def is_valid_pdf(file_url):
    try:
        if any(domain in file_url.lower() for domain in ['ucarecdn.com', 'drive.google.com', 'dropbox.com']):
            return True
        if file_url.lower().endswith('.pdf'):
            return True
        response = requests.head(file_url, timeout=10, allow_redirects=True)
        response.raise_for_status()
        content_type = response.headers.get('content-type', '').lower()
        if 'application/pdf' in content_type:
            return True
        response = requests.get(file_url, stream=True, timeout=10)
        response.raise_for_status()
        first_chunk = next(response.iter_content(chunk_size=4), b'')
        is_pdf = first_chunk.startswith(b'%PDF')
        return is_pdf
    except Exception:
        return True

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "MindFlow backend is running 🚀"})

@app.route('/process-content', methods=['POST'])
def process_content():
    try:
        data = request.get_json()
        
        # Support both 'notes' (from chat frontend) and 'content' (legacy)
        content = data.get('notes') or data.get('content', '')
        content_type = data.get('type', 'text')
        user_info = data.get('user', {})
        
        if not content:
            return jsonify({'error': 'No content provided'}), 400

        print(f"🔄 Processing content: {content_type} ({len(content)} characters)")
        
        # --- Try AI response ---
        ai_response = None
        
        # 1. Try GitHub OpenAI API first
        try:
            if client and github_token:
                resp = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": (
                            "You are Tayyari, an expert educational AI tutor. "
                            "Answer questions clearly and thoroughly using markdown formatting. "
                            "Use headings, bullet points, code blocks where appropriate. "
                            "Always be helpful, accurate, and engaging."
                        )},
                        {"role": "user", "content": content}
                    ],
                    model="openai/gpt-4o",
                    temperature=0.7,
                    max_tokens=2000,
                    top_p=1
                )
                ai_response = resp.choices[0].message.content
                print("✅ Response from GitHub OpenAI API")
        except Exception as e:
            print(f"⚠️ GitHub API failed: {e}")
        
        # 2. Fallback to Gemini
        if not ai_response:
            try:
                prompt = build_prompt_with_heading_and_diagram("AI Answer", content, "📘")
                ai_response = gemini_flash_api.call_gemini_api(prompt)
                if ai_response:
                    print("✅ Response from Gemini API")
            except Exception as e:
                print(f"⚠️ Gemini API failed: {e}")
        
        # 3. Smart fallback response so the UI never shows an error
        if not ai_response:
            print("⚠️ All AI APIs failed — using smart fallback response")
            ai_response = (
                f"## 📚 Your Question\n\n"
                f"> {content[:300]}{'...' if len(content) > 300 else ''}\n\n"
                "---\n\n"
                "## 🤖 Tayyari AI Response\n\n"
                "I received your question but the AI service is temporarily unavailable. "
                "Here's what I can tell you:\n\n"
                "- Your question has been noted and is ready for processing.\n"
                "- Please try again in a moment — our AI services are being restored.\n"
                "- You can also try rephrasing your question for better results.\n\n"
                "**Tip:** If this keeps happening, check that the backend server is running correctly at `http://localhost:5000`.\n"
            )
        
        # Process metadata (keep lightweight)
        summary = ai_response
        key_points = ["AI response generated"]
        quiz_questions = []
        flashcards = []

        # 🏆 LEADERBOARD INTEGRATION - Award points for content processing
        points_awarded = 0
        try:
            if user_info and user_info.get('id'):
                user_id = user_info.get('id')
                username = user_info.get('name', user_info.get('username', f"User {user_id.split('_')[-1] if '_' in user_id else user_id}"))
                email = user_info.get('email', '')
                leaderboard_db.add_user(user_id, username, email)
                points_awarded = 15
                activity_type = 'text_processed'
                if len(content) > 1000:
                    points_awarded += 10
                leaderboard_db.update_user_score(user_id, points_awarded, activity_type)
        except Exception as leaderboard_error:
            print(f"❌ Leaderboard update error: {str(leaderboard_error)}")
        
        # Prepare response — return 'response' key so chat frontend can read it
        response_data = {
            'status': 'success',
            'response': ai_response,
            'message': 'Content processed successfully',
            'data': {
                'summary': summary,
                'key_points': key_points,
                'quiz_questions': quiz_questions,
                'flashcards': flashcards,
                'content_type': content_type,
                'processed_length': len(content),
                'points_awarded': points_awarded,
                'processing_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        print(f"✅ Content processing completed successfully")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Process content error: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'Failed to process content: {str(e)}'
        }), 500


@app.route('/api/quiz/complete', methods=['POST'])
def complete_quiz():
    """Handle quiz completion and award points"""
    try:
        data = request.get_json()
        
        user_info = data.get('user', {})
        quiz_score = data.get('score', 0)  # Score out of 100
        total_questions = data.get('total_questions', 1)
        correct_answers = data.get('correct_answers', 0)
        
        points_awarded = 0
        
        # Award points if user is logged in
        if user_info and user_info.get('id'):
            user_id = user_info.get('id')
            username = user_info.get('name', f"User {user_id.split('_')[-1] if '_' in user_id else user_id}")
            
            # Ensure user exists
            leaderboard_db.add_user(user_id, username)
            
            # Calculate points based on performance
            if quiz_score >= 90:
                points_awarded = 50  # Excellent
            elif quiz_score >= 80:
                points_awarded = 35  # Good
            elif quiz_score >= 70:
                points_awarded = 25  # Fair
            elif quiz_score >= 60:
                points_awarded = 15  # Pass
            else:
                points_awarded = 5   # Participation
            
            # Update scores
            leaderboard_db.update_user_score(user_id, points_awarded, 'quiz_completed')
            leaderboard_db.update_quiz_stats(user_id, quiz_score)
            
            print(f"🎯 Quiz completed: {username} scored {quiz_score}% and earned {points_awarded} points")
        
        return jsonify({
            'status': 'success',
            'message': 'Quiz completed successfully',
            'score': quiz_score,
            'points_awarded': points_awarded
        })
        
    except Exception as e:
        print(f"❌ Quiz completion error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


def award_quiz_points(user_id, username, quiz_score, max_score=100):
    """Award points when user completes a quiz"""
    try:
        # Ensure user exists
        leaderboard_db.add_user(user_id, username)
        
        # Calculate points based on score
        points_earned = 0
        if quiz_score >= max_score * 0.9:  # 90%+
            points_earned = 50
        elif quiz_score >= max_score * 0.8:  # 80%+
            points_earned = 30
        elif quiz_score >= max_score * 0.7:  # 70%+
            points_earned = 20
        else:
            points_earned = 10
        
        # Update scores
        leaderboard_db.update_user_score(user_id, points_earned, 'quiz_completed')
        leaderboard_db.update_quiz_stats(user_id, quiz_score, max_score)
        
        return points_earned
    except Exception as e:
        print(f"Error awarding quiz points: {e}")
        return 0

@app.route("/get-summary", methods=["GET"])
def get_summary():
    summary = agent_service.get_session_summary()
    return jsonify(summary.to_dict())

model = whisper.load_model("base")

@app.route('/speech2text', methods=['POST'])
def transcribe():
    temp_file = "temp_audio.wav"
    if 'file' in request.files:
        file = request.files['file']
        file.save(temp_file)
    elif request.data:
        with open(temp_file, "wb") as f:
            f.write(request.data)
    else:
        return jsonify({"error": "No audio data received"}), 400
    result = model.transcribe(temp_file)
    os.remove(temp_file)  
    return jsonify({"text": result["text"]})

@app.route('/explain-more', methods=['POST'])
def explain_more():
    try:
        data = request.json
        question = data.get('question')
        context = data.get('context', '')
        prompt = build_prompt_with_heading_and_diagram("More About This Topic", context, "🤔")
        response_text = call_gemini_api(prompt, model_override=None)
        if not response_text:
            return jsonify({'error': 'Failed to get response from AI APIs'}), 500
        return jsonify({'response': response_text, 'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/interactive-questions', methods=['POST'])
def interactive_questions():
    try:
        data = request.json
        context = data.get('context', '')
        user_id = data.get('user_id')  # Add this line
        
        prompt = (
            "You are an educational quiz generator.\n"
            "Given the topic below, generate exactly 3 multiple-choice questions in this strict JSON format:\n"
            "[\n"
            " {\n"
            " \"question_text\": \"...\",\n"
            " \"options\": [\"...\", \"...\", \"...\", \"...\"],\n"
            " \"correct_answer\": \"...\",\n"
            " \"explanation\": \"...\",\n"
            " \"diagram\": \"(Provide a Markdown image, ASCII, or visual analogy for this question and explanation, and label it. Render as markdown string.)\"\n"
            " },\n"
            " ...\n"
            "]\n"
            "For each question, the explanation must:\n"
            "- Start with a big heading with an icon\n"
            "- Include the diagram (as markdown)\n"
            "- Then, give the explanation as bullet points (not a paragraph)\n"
            "Return only a JSON array of question objects. Do not add any extra text before or after the array.\n"
            f"Topic: {context}\n"
        )

        response_text = call_gemini_api(prompt, model_override="flash")

        try:
            questions = json.loads(response_text)
        except Exception:
            questions = [{
                "question_text": "Could not generate proper questions.",
                "options": ["Try again", "Contact support"],
                "correct_answer": "Try again",
                "explanation": "There was an error processing the content.",
                "diagram": ""
            }]

        # Award points for content upload if user_id provided
        if user_id:
            points_service.award_content_upload_points(
                user_id=user_id,
                content_type="Quiz Generation",
                content_name=context[:50] + "..." if len(context) > 50 else context
            )

        return jsonify({'questions': questions, 'status': 'success'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/user/initialize', methods=['POST'])
def initialize_user():
    """Initialize user in gamification system"""
    try:
        data = request.json
        user_id = data.get('user_id')
        username = data.get('username', 'Anonymous')
        email = data.get('email', 'unknown@example.com')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Create or update user
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, email, last_active)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, username, email))
        
        conn.commit()
        conn.close()
        
        print(f"✅ User {username} ({user_id}) initialized")
        return jsonify({'status': 'success', 'message': 'User initialized'})
    except Exception as e:
        print(f"❌ Error initializing user: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    """Get user's gamification stats"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Get user stats
        cursor.execute('''
            SELECT user_id, username, email, total_points, level, streak_days,
                   (SELECT COUNT(*) FROM user_badges WHERE user_id = ?) as badges_earned
            FROM users WHERE user_id = ?
        ''', (user_id, user_id))
        
        user_data = cursor.fetchone()
        
        if not user_data:
            # Create user if doesn't exist
            cursor.execute('''
                INSERT INTO users (user_id, username, email) 
                VALUES (?, 'New User', 'user@example.com')
            ''', (user_id,))
            conn.commit()
            
            user_data = (user_id, 'New User', 'user@example.com', 0, 1, 0, 0)
        
        # Get user's rank
        cursor.execute('''
            SELECT COUNT(*) + 1 as rank
            FROM users
            WHERE total_points > (SELECT total_points FROM users WHERE user_id = ?)
        ''', (user_id,))
        rank_result = cursor.fetchone()
        rank = rank_result[0] if rank_result else 1
        
        conn.close()
        
        return jsonify({
            'user_stats': {
                'user_id': user_data[0],
                'username': user_data[1],
                'email': user_data[2],
                'total_points': user_data[3],
                'level': user_data[4],
                'streak_days': user_data[5],
                'badges_earned': user_data[6],
                'current_rank': rank
            }
        })
    except Exception as e:
        print(f"❌ Error getting user stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz_with_points():
    """Submit quiz and award points"""
    try:
        data = request.json
        user_id = data.get('user_id')
        quiz_score = data.get('score', 0.0)  # Score as decimal (0.0 to 1.0)
        quiz_data = data.get('quiz_data', {})
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # Calculate points
        points, activity_type = calculate_quiz_points(quiz_score)
        
        # Check if this is user's first quiz
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM point_transactions 
            WHERE user_id = ? AND activity_type LIKE 'quiz%'
        ''', (user_id,))
        quiz_count = cursor.fetchone()[0]
        conn.close()
        
        is_first_quiz = quiz_count == 0
        if is_first_quiz:
            points += 50  # First-time bonus
        
        # Award points
        description = f"Quiz completed with {int(quiz_score * 100)}% score"
        if is_first_quiz:
            description += " (First Quiz Bonus!)"
            
        transaction_id = award_points(user_id, points, activity_type, description)
        
        # Get updated user stats
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('SELECT total_points, level FROM users WHERE user_id = ?', (user_id,))
        user_stats = cursor.fetchone()
        conn.close()
        
        print(f"🎯 Points awarded: {points} to user {user_id}")
        
        return jsonify({
            'status': 'success',
            'points_awarded': {
                'points_earned': points,
                'transaction_id': transaction_id,
                'activity_type': activity_type,
                'is_first_quiz': is_first_quiz
            },
            'user_stats': {
                'total_points': user_stats[0] if user_stats else 0,
                'level': user_stats[1] if user_stats else 1
            },
            'quiz_score': quiz_score
        })
    except Exception as e:
        print(f"❌ Error submitting quiz: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        time_filter = request.args.get('timeFilter', 'all')
        category = request.args.get('category', 'points')
        user_id = request.args.get('userId')
        
        print(f"📊 Fetching leaderboard: timeFilter={time_filter}, category={category}, userId={user_id}")
        
        # Get leaderboard data
        leaderboard_data = leaderboard_db.get_leaderboard(
            limit=50, 
            time_filter=time_filter, 
            category=category
        )
        
        # Get current user rank if provided
        current_user_rank = None
        if user_id:
            current_user_rank = leaderboard_db.get_user_rank(user_id, category)
            if current_user_rank:
                current_user_rank['isCurrentUser'] = True
                # Get username from Clerk or set default
                current_user_rank['username'] = current_user_rank.get('username', f"User {user_id.split('_')[-1]}")
        
        # Get stats
        stats = leaderboard_db.get_leaderboard_stats()
        
        # Format response
        formatted_leaderboard = []
        for user in leaderboard_data:
            formatted_user = {
                'id': user['user_id'],
                'name': user['username'],
                'points': user['points'],
                'level': user['level'],
                'streak': user['streak'],
                'totalQuizzes': user['total_quizzes'],
                'averageScore': user['average_score'],
                'joinedDate': user['joined_date'][:10] if user['joined_date'] else '2025-01-01',
                'badges': user['badges'],
                'weeklyPoints': user['weekly_points'],
                'monthlyPoints': user['monthly_points'],
                'rank': user['rank'],
                'previousRank': user['previous_rank'] or user['rank'],
                'isCurrentUser': user['user_id'] == user_id
            }
            formatted_leaderboard.append(formatted_user)
        
        return jsonify({
            'status': 'success',
            'leaderboard': formatted_leaderboard,
            'currentUserRank': current_user_rank,
            'stats': stats
        })
    
    except Exception as e:
        print(f"❌ Leaderboard API Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@app.route('/api/leaderboard/update', methods=['POST'])
def update_leaderboard():
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        username = data.get('username', f"User {user_id.split('_')[-1] if '_' in user_id else user_id}")
        email = data.get('email')
        points_earned = data.get('points_earned', 0)
        activity_type = data.get('activity_type', 'general')
        quiz_score = data.get('quiz_score')
        
        # Ensure user exists
        leaderboard_db.add_user(user_id, username, email)
        
        # Update points if provided
        if points_earned > 0:
            leaderboard_db.update_user_score(user_id, points_earned, activity_type)
        
        # Update quiz stats if provided
        if quiz_score is not None:
            leaderboard_db.update_quiz_stats(user_id, quiz_score)
        
        # Get updated user data
        user_data = leaderboard_db.get_user_rank(user_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Leaderboard updated successfully',
            'user_data': user_data
        })
    
    except Exception as e:
        print(f"❌ Update leaderboard error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Initialize database and create sample data
try:
    print("🗄️ Initializing database...")
    create_sample_data()
    print("✅ Database initialization complete!")
except Exception as e:
    print(f"❌ Database initialization error: {str(e)}")


@app.route('/api/leaderboard/populate', methods=['POST'])
def populate_sample_data():
    """Populate database with sample data for testing"""
    try:
        sample_users = [
            {"user_id": "user_001", "username": "Alex Johnson", "email": "alex@example.com"},
            {"user_id": "user_002", "username": "Sarah Chen", "email": "sarah@example.com"},
            {"user_id": "user_003", "username": "Mike Rodriguez", "email": "mike@example.com"},
            {"user_id": "user_004", "username": "Emma Wilson", "email": "emma@example.com"},
            {"user_id": "user_005", "username": "David Kim", "email": "david@example.com"},
            {"user_id": "user_006", "username": "Lisa Zhang", "email": "lisa@example.com"},
            {"user_id": "user_007", "username": "Tom Smith", "email": "tom@example.com"},
            {"user_id": "user_008", "username": "Anna Garcia", "email": "anna@example.com"}
        ]
        
        for user in sample_users:
            # Add user
            leaderboard_db.add_user(user["user_id"], user["username"], user["email"])
            
            # Add random points and activities
            import random
            points = random.randint(100, 3000)
            quizzes = random.randint(5, 50)
            
            leaderboard_db.update_user_score(user["user_id"], points, "sample_data")
            
            # Simulate quiz completions
            for _ in range(quizzes):
                score = random.randint(60, 100)
                leaderboard_db.update_quiz_stats(user["user_id"], score)
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully populated database with {len(sample_users)} sample users'
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Add this to your existing Flask app routes
if __name__ == '__main__':
    print("🚀 Initializing Tayyari.ai backend...")
    
    try:
        print("🗄️ Initializing database...")
        create_sample_data()
        print("✅ Database initialization complete!")
    except Exception as e:
        print(f"❌ Database initialization error: {str(e)}")

    print("🚀 Starting Tayyari.ai backend with leaderboard support on http://localhost:5000...")
    app.run(debug=True, host='0.0.0.0', port=5000)


