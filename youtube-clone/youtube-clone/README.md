# VidTube - YouTube Clone
## Full Backend + Messaging System

A complete YouTube-like video sharing platform with user authentication, video uploads, comments, subscriptions, and real-time direct messaging!

---

## 🚀 QUICK START (5 minutes)

### Step 1: Install Python
Download Python 3.7+ from https://www.python.org/
Make sure to check "Add Python to PATH" during installation

### Step 2: Install Flask
Open Command Prompt/Terminal and run:
```bash
pip install flask
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

### Step 3: Run the App
In Command Prompt/Terminal, navigate to this folder and run:
```bash
python app.py
```

### Step 4: Open Browser
Go to: **http://localhost:5000**

---

## 📁 FOLDER STRUCTURE

```
youtube-clone/
├── app.py                    # Backend Flask server
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html           # Frontend (HTML/CSS/JavaScript)
└── README.md                # This file
```

That's it! No additional setup needed.

---

## ✨ FEATURES

### 👤 User System
- Create account and login
- Edit profile with bio
- View subscriber count
- Channel management

### 🎬 Videos
- Upload videos (with URL)
- View counter
- Video descriptions
- Like/unlike system
- Search videos
- Video feed

### 💬 Comments
- Comment on videos
- View all comments
- Timestamps on comments
- See who commented

### 📨 Direct Messaging
- Message any user
- Full chat history
- Conversation list
- Real-time chat interface

### 🔔 Subscriptions
- Subscribe to channels
- See subscriber count
- Unsubscribe feature

---

## 📝 HOW TO USE

### Create Your First Account
1. Go to http://localhost:5000
2. Click "Create Account"
3. Fill in username, email, password
4. Click "Create Account"
5. Login with your credentials

### Upload a Video
1. Click "📤 Upload" button
2. Fill in:
   - **Title**: Video name
   - **Description**: About the video
   - **Video URL**: Link to MP4 file
3. Click "Upload"

**Free Video URLs to Test:**
- https://commondatastorage.googleapis.com/gtv-videos-library/sample/BigBuckBunny.mp4
- https://commondatastorage.googleapis.com/gtv-videos-library/sample/ElephantsDream.mp4
- https://commondatastorage.googleapis.com/gtv-videos-library/sample/ForBiggerBlazes.mp4

### Watch Videos
1. Click any video on home page
2. See video details, views, likes
3. Scroll down to comments section
4. Click to like the video

### Comment on Videos
1. Watch a video
2. Scroll to comments section
3. Type your comment
4. Click "Post"

### Message Someone
1. Click "💬 Messages" in header
2. Click on a conversation or create new
3. Type message and send (➤)
4. See full chat history

### Edit Profile
1. Click "👤 Profile" in header
2. Click "Edit Profile"
3. Update your bio
4. Click "Save Changes"

### Search Videos
1. Use search bar at top
2. Type title or keywords
3. Click 🔍 button
4. See results

---

## 🛠️ TROUBLESHOOTING

### ❌ "Python not found"
- Reinstall Python from https://www.python.org
- Make sure to check "Add Python to PATH"

### ❌ "Flask not found"
```bash
pip install --upgrade flask
```

### ❌ "Port 5000 already in use"
Edit line 947 in `app.py`:
```python
app.run(debug=True, port=5001)  # Change to 5001
```

### ❌ "Can't see videos when uploaded"
- Check video URL is valid (must be MP4)
- Use example URLs provided above

### ❌ "Database error"
- Delete `youtubeclone.db` file
- Restart the app

### ❌ "Can't send messages"
- Make sure both users have accounts created
- Create 2 test accounts to test messaging

---

## 📊 DATABASE

The app automatically creates `youtubeclone.db` with these tables:
- **users** - User accounts
- **videos** - Video metadata
- **comments** - Video comments
- **messages** - Direct messages
- **conversations** - Chat groups
- **subscriptions** - User subscriptions
- **video_likes** - Video likes
- **playlists** - Playlists

No setup needed! Database is created automatically.

---

## 🔐 SECURITY NOTE

This is an educational/demo project. For production use:
- Change secret key (line 19 in app.py)
- Use bcrypt for passwords
- Add HTTPS/SSL
- Add rate limiting
- Validate all inputs
- Use environment variables

---

## 📱 KEYBOARD SHORTCUTS

| Action | Command |
|--------|---------|
| Home | Click logo |
| Upload | Ctrl/Cmd + U (via Upload button) |
| Messages | Click Messages button |
| Profile | Click Profile button |
| Logout | Click Logout button |

---

## 🆘 NEED HELP?

1. Check that Flask is installed:
   ```bash
   pip list | grep flask
   ```

2. Make sure folder structure is correct:
   ```
   youtube-clone/
   ├── app.py
   └── templates/
       └── index.html
   ```

3. Check browser console (F12) for JavaScript errors

4. Check terminal for Flask errors

---

## 💡 TIPS FOR TESTING

**Test Multiple Users:**
1. Create account 1: username: "john", password: "password123"
2. Create account 2: username: "jane", password: "password123"
3. Switch between accounts to test messaging
4. Each user can upload videos and comment

**Test Messaging:**
1. Login as user 1
2. Go to Messages
3. Start new conversation with user 2
4. Type and send messages
5. Login as user 2 to see messages

**Test Video Features:**
1. Upload video as user 1
2. Login as user 2
3. Like the video
4. Comment on the video
5. Subscribe to user 1's channel

---

## 📝 API ENDPOINTS (For Developers)

```
POST   /api/auth/register         - Create account
POST   /api/auth/login            - Login
GET    /api/auth/me               - Current user
GET    /api/videos                - Get all videos
GET    /api/videos/<id>           - Get video details
POST   /api/videos                - Upload video
POST   /api/videos/<id>/like      - Like video
POST   /api/videos/<id>/comments  - Add comment
GET    /api/search                - Search videos
GET    /api/users/<id>            - Get user profile
PUT    /api/users/<id>/bio        - Update bio
POST   /api/users/<id>/subscribe  - Subscribe
GET    /api/messages/<user_id>    - Get chat history
POST   /api/messages/<user_id>    - Send message
GET    /api/conversations         - Get conversations
```

---

## 🚀 DEPLOYMENT

To deploy to production:

### Heroku
1. Create Heroku account
2. Install Heroku CLI
3. Run: `heroku create youtube-clone`
4. Run: `git push heroku main`

### PythonAnywhere
1. Create account at pythonanywhere.com
2. Upload files
3. Configure web app
4. Start the app

### AWS
1. EC2 instance with Python
2. Install Flask
3. Use Gunicorn as WSGI server
4. Set up nginx as reverse proxy

---

## 📄 FILE INFO

- **app.py** - 950+ lines of Flask backend code
- **index.html** - 1600+ lines of HTML/CSS/JavaScript frontend
- **requirements.txt** - Python dependencies

---

## 🎯 FUTURE FEATURES

- [ ] Video streaming with buffering
- [ ] Real-time notifications
- [ ] Video recommendations
- [ ] Trending algorithm
- [ ] User verification
- [ ] Video transcoding
- [ ] CDN integration
- [ ] Mobile app
- [ ] Live streaming
- [ ] Monetization

---

## 📜 LICENSE

This is an educational project. Use and modify freely for learning!

---

## 🎬 ENJOY!

You now have a fully functional YouTube clone!

**Questions?** Check the troubleshooting section above.

**Happy streaming!** 🎥🍿
