# 🚀 Quick Setup Guide

Get PulsePoint AI running in under 5 minutes!

## Prerequisites

Before starting, make sure you have:

- [ ] Python 3.8 or higher installed
  ```bash
  python --version  # Should show 3.8+
  ```

- [ ] FFmpeg installed
  ```bash
  ffmpeg -version  # Should show FFmpeg version
  ```

- [ ] OpenAI API Key - [Get it here](https://platform.openai.com/api-keys)
- [ ] Google AI API Key - [Get it here](https://makersuite.google.com/app/apikey)

---

## Step-by-Step Setup

### 1️⃣ Install FFmpeg

#### macOS
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Windows
1. Download from https://ffmpeg.org/download.html
2. Extract and add to PATH
3. Verify with `ffmpeg -version`

### 2️⃣ Clone and Navigate
```bash
git clone https://github.com/YOUR_USERNAME/pulsepoint-ai.git
cd pulsepoint-ai
```

### 3️⃣ Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

Your terminal should now show `(venv)` at the beginning.

### 4️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

This will take 2-3 minutes. Perfect time for a coffee! ☕

### 5️⃣ Configure API Keys

```bash
# Copy the template
cp .env.example .env

# Edit the file
nano .env  # or use your favorite editor
```

Add your API keys:
```env
OPENAI_API_KEY=sk-proj-...your-actual-key...
GOOGLE_API_KEY=AIza...your-actual-key...
```

**Important**: These keys are secret! Never commit them to git.

### 6️⃣ Run the Application

```bash
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

### 7️⃣ Open the Frontend

Open `frontend/index.html` in your web browser.

---

## 🧪 Test It Out

### Option 1: Use the Web Interface
1. Open `frontend/index.html`
2. Drag and drop a video file
3. Watch the magic happen!

### Option 2: Use the Test Script
```bash
python test_api.py
```

Follow the prompts to upload a video and see the results.

### Option 3: Test with Sample Video

Download the hackathon sample video and process it:
```bash
# Download sample video
curl -L "SAMPLE_VIDEO_URL" -o sample_video.mp4

# Run test script
python test_api.py
# Choose option 3 (Use test sample)
```

---

## ✅ Verification Checklist

Make sure everything works:

- [ ] Server starts without errors
- [ ] Frontend loads in browser
- [ ] Health check shows API keys configured
  - Visit: http://localhost:8000/health
- [ ] Can upload a video
- [ ] Processing completes successfully
- [ ] Can download generated clips
- [ ] Clips are in vertical format (9:16)
- [ ] Clips have captions

---

## 🐛 Common Issues

### Issue: "ModuleNotFoundError: No module named 'backend'"

**Solution**: Make sure you're running from the project root directory:
```bash
pwd  # Should end with /pulsepoint-ai
```

### Issue: "API keys not configured"

**Solution**:
1. Check `.env` file exists: `ls -la .env`
2. Verify keys are set: `cat .env` (don't share output!)
3. Restart server after changing .env

### Issue: "FFmpeg not found"

**Solution**: Install FFmpeg (see Step 1) and verify:
```bash
ffmpeg -version
```

### Issue: Port 8000 already in use

**Solution**:
```bash
# Find what's using port 8000
lsof -i :8000

# Kill that process or use a different port
# Edit .env and change PORT=8001
```

### Issue: "CERTIFICATE_VERIFY_FAILED" (macOS)

**Solution**:
```bash
# Install certificates
/Applications/Python\ 3.x/Install\ Certificates.command
```

### Issue: Processing takes forever

**Solution**:
- First run downloads AI models (one-time, ~500MB)
- Check logs for progress
- Ensure stable internet connection
- Try with a shorter video first

---

## 🎯 Next Steps

Now that it's running:

1. **Try Different Videos**
   - Upload various types of content
   - See how the AI adapts

2. **Explore the API**
   - Check out http://localhost:8000/docs
   - See all available endpoints
   - Try the interactive API documentation

3. **Customize Settings**
   - Edit `.env` to adjust:
     - Number of clips (MAX_CLIPS)
     - Clip duration (MIN/MAX_CLIP_DURATION)
     - Other parameters

4. **Review the Output**
   - Check `outputs/` folder for clips
   - Review `*_metadata.json` for analysis details
   - See what moments the AI identified

---

## 📚 Learn More

- [Full README](README.md) - Complete documentation
- [Demo Instructions](DEMO_INSTRUCTIONS.md) - How to record your demo
- [API Documentation](http://localhost:8000/docs) - Interactive API docs

---

## 💡 Pro Tips

### Tip 1: Use a Short Test Video First
Before processing hour-long videos, test with a 5-minute clip to verify everything works.

### Tip 2: Check the Logs
The server outputs detailed logs. Watch them to understand the processing pipeline.

### Tip 3: Save API Costs
- Start with Gemini's free tier (60 requests/minute)
- Use shorter videos during testing
- The system caches some results

### Tip 4: GPU Acceleration (Advanced)
For faster processing, install GPU-accelerated libraries:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Tip 5: Docker (Advanced)
Want to containerize? Here's a quick Dockerfile:
```dockerfile
FROM python:3.10-slim
RUN apt-get update && apt-get install -y ffmpeg
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

---

## 🎉 You're All Set!

PulsePoint AI is now ready to transform your long-form videos into viral clips!

Need help? Check the troubleshooting section above or review the main [README](README.md).

Happy hacking! 🚀
