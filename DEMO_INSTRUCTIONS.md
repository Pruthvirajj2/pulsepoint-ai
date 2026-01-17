# 📹 Demo Video Recording Instructions

To complete your hackathon submission, you need to record a screen recording video demonstrating the working application.

## 🎯 What to Include in Your Demo Video

### 1. Introduction (30 seconds)
- Show the README on screen
- Briefly explain what PulsePoint AI does
- Mention the key features:
  - Emotional peak detection
  - AI-powered moment selection
  - Smart vertical cropping
  - Dynamic captions

### 2. Setup Demonstration (30 seconds)
- Show the project structure
- Highlight key files:
  - `backend/video_processor.py`
  - `backend/audio_analyzer.py`
  - `backend/ai_analyzer.py`
  - `backend/face_tracker.py`
- Show the `.env` file (blur out actual API keys!)

### 3. Running the Application (30 seconds)
- Open terminal
- Run: `python run.py`
- Show the server starting up successfully
- Open `frontend/index.html` in browser

### 4. Core Demo - Upload & Process (2-3 minutes)
- Show the beautiful UI
- Upload the test video (or use URL)
- Show the real-time progress updates:
  - "Uploading video..."
  - "Analyzing audio for emotional peaks..."
  - "Transcribing with Whisper..."
  - "Using Gemini AI to identify best moments..."
  - "Creating video clips..."
- Point out the percentage progress bar

### 5. Results Showcase (1-2 minutes)
- Show the generated clips in the UI
- Highlight for each clip:
  - The catchy headline
  - Emotional appeal badge
  - Duration
- Download one or two clips
- Open and play the downloaded clips to show:
  - Vertical 9:16 format
  - Face-centered cropping
  - Dynamic caption overlay
  - High quality output

### 6. Technical Deep Dive (Optional - 1 minute)
- Show the JSON metadata file
- Highlight the analysis results:
  - Emotional peaks detected
  - AI-identified moments
  - Timestamps and scores
- Show logs demonstrating the processing pipeline

### 7. Conclusion (30 seconds)
- Recap the key achievements:
  - Full implementation of all features
  - Multi-modal AI approach
  - Production-ready code
  - Beautiful user experience
- Show the GitHub repository
- Thank the judges!

## 🛠️ Recording Tools

### macOS
- **QuickTime Player** (Built-in, free)
  - Open QuickTime Player
  - File → New Screen Recording
  - Record your screen

- **OBS Studio** (Free, professional)
  - Download from https://obsproject.com
  - More control over recording quality

### Windows
- **Xbox Game Bar** (Built-in, free)
  - Press `Win + G`
  - Click record button

- **OBS Studio** (Free, professional)
  - Download from https://obsproject.com

### Linux
- **SimpleScreenRecorder** (Free)
  - `sudo apt install simplescreenrecorder`

- **OBS Studio** (Free)
  - Available in most package managers

## 📝 Recording Tips

1. **Resolution**: Record in at least 1080p (1920x1080)
2. **Audio**: Make sure to narrate what you're doing (optional but recommended)
3. **Clean Desktop**: Hide personal information and unnecessary windows
4. **Internet**: Disable notifications during recording
5. **Duration**: Aim for 4-6 minutes total
6. **Blur Sensitive Info**:
   - API keys in .env file
   - Personal information
   - Email addresses

## ✂️ Video Editing (Optional)

If you want to polish your demo:

### Free Tools
- **DaVinci Resolve** (Windows/Mac/Linux)
  - Professional-grade, completely free
  - https://www.blackmagicdesign.com/products/davinciresolve

- **Shotcut** (Windows/Mac/Linux)
  - Simple and open-source
  - https://shotcut.org

- **iMovie** (Mac only)
  - Built-in, user-friendly

### Simple Edits to Consider
- Cut out any mistakes or pauses
- Add text overlays for key points
- Speed up slow sections (like installation)
- Add intro/outro screens

## 📤 Uploading Your Demo

1. **YouTube** (Recommended)
   - Upload as unlisted video
   - Add to README: `[Watch Demo](https://youtube.com/...)`

2. **Google Drive**
   - Upload video
   - Set sharing to "Anyone with the link"
   - Add link to README

3. **Loom** (Easy option)
   - Record directly with Loom: https://loom.com
   - Automatically generates shareable link

## 📋 Demo Script Template

Use this as a guide while recording:

```
[00:00 - 00:30] Introduction
"Hi! This is PulsePoint AI, my submission for the ByteSize Sage AI Hackathon.
It transforms long-form videos into viral short-form content using multi-modal AI.
Let me show you how it works."

[00:30 - 01:00] Setup
"Here's the project structure. The backend uses FastAPI with multiple AI services.
We have audio analysis with Librosa, transcription with Whisper,
content analysis with Gemini, and face tracking with MediaPipe."

[01:00 - 01:30] Starting the app
"Let me start the server with our run script.
And here's the beautiful web interface built with Pico.css."

[01:30 - 04:00] Main demo
"Now I'll upload a video... [upload]
Watch as it processes in real-time...
The system is analyzing the audio for emotional peaks,
transcribing with Whisper, and using Gemini AI to identify the best moments."

[04:00 - 05:30] Results
"And here are our generated clips! Each one has a catchy headline,
emotional appeal tagging, and optimized duration.
Let me download one and show you..."

[Video plays - vertical format, face-centered, with caption]

"Perfect! Vertical format, the speaker is centered, and we have
the dynamic caption overlay."

[05:30 - 06:00] Conclusion
"PulsePoint AI successfully implements all the hackathon requirements
plus optional features, using a sophisticated multi-modal AI pipeline.
Thank you for watching!"
```

## ✅ Pre-Recording Checklist

- [ ] Application runs without errors
- [ ] .env file configured (with API keys blurred)
- [ ] Test video ready to upload
- [ ] Desktop cleaned and organized
- [ ] Notifications disabled
- [ ] Recording software tested
- [ ] Internet connection stable
- [ ] Good lighting (if showing yourself)
- [ ] Quiet environment (if recording audio)

## 🎬 Final Check

Before uploading, watch your recording and verify:
- [ ] Audio is clear (if narrating)
- [ ] Screen is clearly visible
- [ ] No sensitive information shown
- [ ] All key features demonstrated
- [ ] Generated clips are shown working
- [ ] Video quality is good (1080p+)
- [ ] Duration is 4-6 minutes

## 📌 Adding Video to README

After uploading, update your README.md:

```markdown
## 🎬 Demo Video

**Watch the full demo here**: [PulsePoint AI Demo](YOUR_VIDEO_LINK)

<video width="100%" controls>
  <source src="YOUR_VIDEO_LINK" type="video/mp4">
</video>
```

---

Good luck with your demo! Make it shine! ⭐
