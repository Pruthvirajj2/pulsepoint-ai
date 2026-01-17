# 🚀 Quick Start Guide - You're Almost Ready!

Your API keys are configured! Just 3 more steps:

## ✅ What's Already Done

- ✅ API keys configured (AssemblyAI + Google Gemini)
- ✅ Code updated to use **FREE** AssemblyAI (100 hours/month!)
- ✅ Project structure complete

---

## 🔧 Step 1: Install FFmpeg (Required)

FFmpeg is needed for video processing.

### macOS:
```bash
brew install ffmpeg
```

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install ffmpeg
```

### Verify Installation:
```bash
ffmpeg -version
```

---

## 📦 Step 2: Install Python Dependencies

```bash
cd /Users/pruthwiraj.chandruboomi.com/ess/x/pulsepoint-ai

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies (takes 2-3 minutes)
pip install -r requirements.txt
```

---

## 🎬 Step 3: Run the Application

```bash
# Make sure you're still in the virtual environment
# (you should see (venv) at the start of your terminal prompt)

python run.py
```

You should see:
```
╔════════════════════════════════════════════════════════╗
║                  PulsePoint AI                         ║
║              Starting Application Server               ║
╚════════════════════════════════════════════════════════╝

🚀 Starting server on http://localhost:8000
```

---

## 🌐 Step 4: Open the Web Interface

Open this file in your browser:
```
/Users/pruthwiraj.chandruboomi.com/ess/x/pulsepoint-ai/frontend/index.html
```

Or just double-click `frontend/index.html`

---

## 🧪 Test It!

1. **Upload a test video** (any MP4 file, even 1-2 minutes is fine)
2. **Watch the progress** - Real-time updates as it processes
3. **Download your clips** - Get 3-5 viral-ready vertical videos!

---

## 💡 Quick Commands

### Check if everything is installed:
```bash
# Check Python
python3 --version

# Check FFmpeg
ffmpeg -version

# Check if virtual environment is active
which python  # Should show path with 'venv'
```

### Restart the server:
```bash
# Stop: Press Ctrl+C
# Start again:
python run.py
```

### Check API keys are loaded:
```bash
# Visit this URL in browser:
http://localhost:8000/health

# Should show:
# {
#   "status": "healthy",
#   "api_keys_configured": {
#     "assemblyai": true,
#     "google": true
#   }
# }
```

---

## 🎉 Why Your Setup is Special

You're using **100% FREE APIs**:
- ✅ **AssemblyAI**: 100 hours/month FREE (no payment needed!)
- ✅ **Google Gemini**: 60 requests/min FREE
- ✅ **Total Cost**: $0.00

This is perfect for the hackathon and way better than OpenAI's paid API!

---

## 🐛 Troubleshooting

### "Command not found: ffmpeg"
→ Install FFmpeg (see Step 1 above)

### "No module named 'fastapi'"
→ Make sure virtual environment is activated:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Server won't start
→ Check if port 8000 is free:
```bash
lsof -i :8000
# If something is using it, kill it or change PORT in .env
```

### "API keys not configured"
→ Your keys are already in `.env`, just restart the server:
```bash
# Press Ctrl+C to stop
python run.py  # Start again
```

---

## 📞 Need Help?

Your `.env` file is already configured with:
- AssemblyAI API Key: `f7cd087ac6634e06adebfbeaac3a16d2`
- Google API Key: `AIzaSyBrACjjDEFgBsP8re7r_PJzNBNEXdt4UsU`

Just install FFmpeg and Python dependencies, then run!

---

**Ready? Let's do this! 🚀**

```bash
# One-liner to get started (after installing FFmpeg):
cd /Users/pruthwiraj.chandruboomi.com/ess/x/pulsepoint-ai && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python run.py
```
