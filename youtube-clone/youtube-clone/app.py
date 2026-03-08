import sqlite3
import os
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, send_file, session
import threading
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Database setup
DB_PATH = 'youtubeclone.db'

def init_db():
    """Initialize database with all tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        profile_pic TEXT,
        bio TEXT,
        subscribers INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Videos table
    c.execute('''CREATE TABLE IF NOT EXISTS videos (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        filename TEXT NOT NULL,
        thumbnail TEXT,
        views INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        duration INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Comments table
    c.execute('''CREATE TABLE IF NOT EXISTS comments (
        id TEXT PRIMARY KEY,
        video_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        text TEXT NOT NULL,
        likes INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (video_id) REFERENCES videos(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Subscriptions table
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
        id TEXT PRIMARY KEY,
        subscriber_id TEXT NOT NULL,
        channel_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(subscriber_id, channel_id),
        FOREIGN KEY (subscriber_id) REFERENCES users(id),
        FOREIGN KEY (channel_id) REFERENCES users(id)
    )''')
    
    # Messages table (for direct messaging)
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        sender_id TEXT NOT NULL,
        receiver_id TEXT NOT NULL,
        text TEXT NOT NULL,
        read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id)
    )''')
    
    # Conversations table (for chat grouping)
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        user1_id TEXT NOT NULL,
        user2_id TEXT NOT NULL,
        last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user1_id, user2_id),
        FOREIGN KEY (user1_id) REFERENCES users(id),
        FOREIGN KEY (user2_id) REFERENCES users(id)
    )''')
    
    # Video likes table
    c.execute('''CREATE TABLE IF NOT EXISTS video_likes (
        id TEXT PRIMARY KEY,
        video_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(video_id, user_id),
        FOREIGN KEY (video_id) REFERENCES videos(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Playlists table
    c.execute('''CREATE TABLE IF NOT EXISTS playlists (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    """Decorator for routes that require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ========== AUTHENTICATION ROUTES ==========

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not all([username, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    try:
        conn = get_db()
        c = conn.cursor()
        
        user_id = str(uuid.uuid4())
        hashed_pwd = hash_password(password)
        
        c.execute('''INSERT INTO users (id, username, email, password, bio)
                   VALUES (?, ?, ?, ?, ?)''',
                (user_id, username, email, hashed_pwd, 'Welcome to my channel!'))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Registration successful',
            'user_id': user_id,
            'username': username
        }), 201
    
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username or email already exists'}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not all([username, password]):
        return jsonify({'error': 'Missing credentials'}), 400
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    
    if not user or user['password'] != hash_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    session['user_id'] = user['id']
    session['username'] = user['username']
    
    return jsonify({
        'message': 'Login successful',
        'user_id': user['id'],
        'username': user['username']
    }), 200

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'message': 'Logged out'}), 200

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current logged in user"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, username, email, bio, subscribers FROM users WHERE id = ?',
             (session['user_id'],))
    user = c.fetchone()
    conn.close()
    
    return jsonify({
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'bio': user['bio'],
        'subscribers': user['subscribers']
    }), 200

# ========== USER PROFILE ROUTES ==========

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, username, bio, subscribers, created_at FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user's videos
    c.execute('SELECT id, title, views, created_at FROM videos WHERE user_id = ? ORDER BY created_at DESC',
             (user_id,))
    videos = [dict(v) for v in c.fetchall()]
    conn.close()
    
    return jsonify({
        'id': user['id'],
        'username': user['username'],
        'bio': user['bio'],
        'subscribers': user['subscribers'],
        'video_count': len(videos),
        'created_at': user['created_at'],
        'videos': videos
    }), 200

@app.route('/api/users/<user_id>/bio', methods=['PUT'])
@login_required
def update_bio(user_id):
    """Update user bio"""
    if session['user_id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    bio = data.get('bio', '').strip()[:500]
    
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET bio = ? WHERE id = ?', (bio, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Bio updated'}), 200

# ========== VIDEO ROUTES ==========

@app.route('/api/videos', methods=['GET'])
def get_videos():
    """Get all videos (homepage feed)"""
    page = request.args.get('page', 1, type=int)
    limit = 12
    offset = (page - 1) * limit
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''SELECT v.id, v.title, v.description, v.views, v.likes, v.created_at,
                        u.username, u.id as user_id
                 FROM videos v
                 JOIN users u ON v.user_id = u.id
                 ORDER BY v.created_at DESC
                 LIMIT ? OFFSET ?''', (limit, offset))
    
    videos = [dict(v) for v in c.fetchall()]
    conn.close()
    
    return jsonify(videos), 200

@app.route('/api/videos/<video_id>', methods=['GET'])
def get_video(video_id):
    """Get single video details"""
    conn = get_db()
    c = conn.cursor()
    
    # Get video info
    c.execute('''SELECT v.*, u.username, u.id as user_id, u.subscribers
                 FROM videos v
                 JOIN users u ON v.user_id = u.id
                 WHERE v.id = ?''', (video_id,))
    
    video = c.fetchone()
    
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    # Increment views
    c.execute('UPDATE videos SET views = views + 1 WHERE id = ?', (video_id,))
    
    # Get comments
    c.execute('''SELECT c.id, c.text, c.likes, c.created_at, u.username, u.id as user_id
                 FROM comments c
                 JOIN users u ON c.user_id = u.id
                 WHERE c.video_id = ?
                 ORDER BY c.created_at DESC''', (video_id,))
    
    comments = [dict(c) for c in c.fetchall()]
    
    conn.commit()
    conn.close()
    
    video_dict = dict(video)
    video_dict['comments'] = comments
    
    return jsonify(video_dict), 200

@app.route('/api/videos', methods=['POST'])
@login_required
def upload_video():
    """Upload a new video"""
    data = request.get_json()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    video_url = data.get('video_url', '')
    
    if not title or not video_url:
        return jsonify({'error': 'Title and video URL required'}), 400
    
    video_id = str(uuid.uuid4())
    
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO videos (id, user_id, title, description, filename)
               VALUES (?, ?, ?, ?, ?)''',
            (video_id, session['user_id'], title, description, video_url))
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': 'Video uploaded',
        'video_id': video_id
    }), 201

@app.route('/api/videos/<video_id>/like', methods=['POST'])
@login_required
def like_video(video_id):
    """Like a video"""
    conn = get_db()
    c = conn.cursor()
    
    like_id = str(uuid.uuid4())
    
    try:
        c.execute('''INSERT INTO video_likes (id, video_id, user_id)
                   VALUES (?, ?, ?)''',
                (like_id, video_id, session['user_id']))
        c.execute('UPDATE videos SET likes = likes + 1 WHERE id = ?', (video_id,))
        conn.commit()
        
        return jsonify({'message': 'Video liked'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Already liked'}), 400
    finally:
        conn.close()

@app.route('/api/videos/<video_id>/comments', methods=['POST'])
@login_required
def add_comment(video_id):
    """Add a comment to a video"""
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text or len(text) > 1000:
        return jsonify({'error': 'Invalid comment'}), 400
    
    comment_id = str(uuid.uuid4())
    
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO comments (id, video_id, user_id, text)
               VALUES (?, ?, ?, ?)''',
            (comment_id, video_id, session['user_id'], text))
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': 'Comment added',
        'comment_id': comment_id
    }), 201

@app.route('/api/search', methods=['GET'])
def search_videos():
    """Search for videos"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'error': 'Query too short'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    search_term = f"%{query}%"
    c.execute('''SELECT v.id, v.title, v.description, v.views, v.likes, u.username, u.id as user_id
                 FROM videos v
                 JOIN users u ON v.user_id = u.id
                 WHERE v.title LIKE ? OR v.description LIKE ?
                 ORDER BY v.views DESC
                 LIMIT 20''', (search_term, search_term))
    
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    
    return jsonify(results), 200

# ========== SUBSCRIPTION ROUTES ==========

@app.route('/api/users/<channel_id>/subscribe', methods=['POST'])
@login_required
def subscribe(channel_id):
    """Subscribe to a channel"""
    if session['user_id'] == channel_id:
        return jsonify({'error': 'Cannot subscribe to yourself'}), 400
    
    subscription_id = str(uuid.uuid4())
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        c.execute('''INSERT INTO subscriptions (id, subscriber_id, channel_id)
                   VALUES (?, ?, ?)''',
                (subscription_id, session['user_id'], channel_id))
        c.execute('UPDATE users SET subscribers = subscribers + 1 WHERE id = ?', (channel_id,))
        conn.commit()
        return jsonify({'message': 'Subscribed'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Already subscribed'}), 400
    finally:
        conn.close()

@app.route('/api/users/<channel_id>/subscribers', methods=['GET'])
def get_subscribers(channel_id):
    """Get channel subscribers"""
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT u.id, u.username
                 FROM subscriptions s
                 JOIN users u ON s.subscriber_id = u.id
                 WHERE s.channel_id = ?''', (channel_id,))
    
    subscribers = [dict(s) for s in c.fetchall()]
    conn.close()
    
    return jsonify(subscribers), 200

# ========== MESSAGING ROUTES ==========

@app.route('/api/messages/<other_user_id>', methods=['GET'])
@login_required
def get_messages(other_user_id):
    """Get messages with another user"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''SELECT * FROM messages
                 WHERE (sender_id = ? AND receiver_id = ?)
                    OR (sender_id = ? AND receiver_id = ?)
                 ORDER BY created_at ASC
                 LIMIT 50''',
            (session['user_id'], other_user_id, other_user_id, session['user_id']))
    
    messages = [dict(m) for m in c.fetchall()]
    
    # Mark messages as read
    c.execute('''UPDATE messages SET read = 1
                 WHERE receiver_id = ? AND sender_id = ?''',
            (session['user_id'], other_user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify(messages), 200

@app.route('/api/messages/<receiver_id>', methods=['POST'])
@login_required
def send_message(receiver_id):
    """Send a message to another user"""
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text or len(text) > 2000:
        return jsonify({'error': 'Invalid message'}), 400
    
    message_id = str(uuid.uuid4())
    
    conn = get_db()
    c = conn.cursor()
    
    # Insert message
    c.execute('''INSERT INTO messages (id, sender_id, receiver_id, text)
               VALUES (?, ?, ?, ?)''',
            (message_id, session['user_id'], receiver_id, text))
    
    # Update or create conversation
    user1, user2 = min(session['user_id'], receiver_id), max(session['user_id'], receiver_id)
    
    try:
        conv_id = str(uuid.uuid4())
        c.execute('''INSERT INTO conversations (id, user1_id, user2_id)
                   VALUES (?, ?, ?)''', (conv_id, user1, user2))
    except sqlite3.IntegrityError:
        pass
    
    c.execute('''UPDATE conversations SET last_message_at = CURRENT_TIMESTAMP
                 WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)''',
            (user1, user2, user2, user1))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': 'Message sent',
        'message_id': message_id
    }), 201

@app.route('/api/conversations', methods=['GET'])
@login_required
def get_conversations():
    """Get list of conversations"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''SELECT DISTINCT
                    CASE WHEN user1_id = ? THEN user2_id ELSE user1_id END as other_user_id,
                    last_message_at
                 FROM conversations
                 WHERE user1_id = ? OR user2_id = ?
                 ORDER BY last_message_at DESC''',
            (session['user_id'], session['user_id'], session['user_id']))
    
    conversation_rows = c.fetchall()
    conversations = []
    
    for row in conversation_rows:
        other_id = row['other_user_id']
        c.execute('SELECT username FROM users WHERE id = ?', (other_id,))
        user = c.fetchone()
        if user:
            conversations.append({
                'user_id': other_id,
                'username': user['username'],
                'last_message_at': row['last_message_at']
            })
    
    conn.close()
    
    return jsonify(conversations), 200

@app.route('/api/messages/unread', methods=['GET'])
@login_required
def get_unread_count():
    """Get count of unread messages"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) as count FROM messages WHERE receiver_id = ? AND read = 0',
             (session['user_id'],))
    
    result = c.fetchone()
    conn.close()
    
    return jsonify({'unread_count': result['count']}), 200

# ========== HOMEPAGE ==========

@app.route('/')
def index():
    """Serve the frontend"""
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    print("✅ Database initialized")
    print("🚀 Starting YouTube Clone Server on http://localhost:5000")
    app.run(debug=True, port=5000)
