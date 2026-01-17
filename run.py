#!/usr/bin/env python3
"""
Simple runner script for PulsePoint AI
"""
import sys
import subprocess
from pathlib import Path


def check_env_file():
    """Check if .env file exists"""
    env_file = Path('.env')

    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("\nCreating .env file from template...")

        # Copy from example
        example_file = Path('.env.example')
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("✅ .env file created")
            print("\n⚠️  IMPORTANT: Please edit .env and add your API keys:")
            print("   - ASSEMBLYAI_API_KEY (100% FREE!)")
            print("   - GOOGLE_API_KEY (100% FREE!)")
            print("\nThen run this script again.")
            sys.exit(1)
        else:
            print("❌ .env.example not found!")
            sys.exit(1)


def check_dependencies():
    """Check if dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import moviepy
        import librosa
        import requests  # for AssemblyAI API
        import google.generativeai
        import mediapipe
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        return False


def start_server():
    """Start the FastAPI server"""
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║                  PulsePoint AI                         ║
    ║              Starting Application Server               ║
    ╚════════════════════════════════════════════════════════╝
    """)

    print("🚀 Starting server on http://localhost:8000")
    print("\n📋 Next steps:")
    print("   1. Keep this terminal window open")
    print("   2. Open frontend/index.html in your browser")
    print("   3. Upload a video and watch the magic happen!")
    print("\n💡 Press Ctrl+C to stop the server\n")
    print("=" * 60 + "\n")

    # Start uvicorn
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])


def main():
    """Main entry point"""
    # Check environment
    check_env_file()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Start server
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
