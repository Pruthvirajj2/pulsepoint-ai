"""
Test script for PulsePoint AI
Demonstrates API usage and functionality
"""
import requests
import time
import json
from pathlib import Path


API_BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_health_check():
    """Test the health check endpoint"""
    print_section("Testing Health Check")

    response = requests.get(f"{API_BASE_URL}/health")
    data = response.json()

    print(f"Status: {data['status']}")
    print(f"API Keys Configured:")
    print(f"  OpenAI: {data['api_keys_configured']['openai']}")
    print(f"  Google: {data['api_keys_configured']['google']}")

    return data['api_keys_configured']['openai'] and data['api_keys_configured']['google']


def upload_video(video_path):
    """Upload a video file"""
    print_section(f"Uploading Video: {video_path}")

    if not Path(video_path).exists():
        print(f"❌ Error: Video file not found at {video_path}")
        return None

    with open(video_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_BASE_URL}/api/upload", files=files)

    data = response.json()

    if data['success']:
        print(f"✅ Upload successful!")
        print(f"Job ID: {data['job_id']}")
        return data['job_id']
    else:
        print(f"❌ Upload failed: {data.get('message', 'Unknown error')}")
        return None


def process_video_url(video_url):
    """Process video from URL"""
    print_section(f"Processing Video from URL")

    response = requests.post(
        f"{API_BASE_URL}/api/process-url",
        json={'video_url': video_url}
    )

    data = response.json()

    if data['success']:
        print(f"✅ Processing started!")
        print(f"Job ID: {data['job_id']}")
        return data['job_id']
    else:
        print(f"❌ Failed to start processing: {data.get('message', 'Unknown error')}")
        return None


def monitor_job_status(job_id):
    """Monitor job status until completion"""
    print_section(f"Monitoring Job: {job_id}")

    last_progress = -1

    while True:
        response = requests.get(f"{API_BASE_URL}/api/status/{job_id}")
        data = response.json()

        status = data['status']
        progress = data.get('progress', 0)
        message = data.get('message', '')

        # Only print if progress changed
        if progress != last_progress:
            print(f"[{progress}%] {message}")
            last_progress = progress

        if status == 'completed':
            print("\n✅ Processing completed successfully!")
            return data
        elif status == 'failed':
            print(f"\n❌ Processing failed: {message}")
            return None

        time.sleep(2)


def download_clips(job_id, clips, output_dir="downloads"):
    """Download all generated clips"""
    print_section("Downloading Clips")

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    for clip in clips:
        clip_index = clip['index']
        filename = clip['filename']
        local_path = output_path / filename

        print(f"\nDownloading Clip {clip_index}: {clip['headline']}")
        print(f"  Duration: {clip['duration']:.1f}s")
        print(f"  Emotional Appeal: {clip['emotional_appeal']}")

        # Download file
        response = requests.get(
            f"{API_BASE_URL}/api/download/{job_id}/{clip_index}",
            stream=True
        )

        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"  ✅ Saved to: {local_path}")
        else:
            print(f"  ❌ Download failed with status {response.status_code}")

    print(f"\n🎉 All clips downloaded to: {output_path.absolute()}")


def display_results(result_data):
    """Display processing results"""
    print_section("Processing Results")

    clips = result_data.get('clips', [])

    print(f"\n📊 Generated {len(clips)} clips:\n")

    for clip in clips:
        print(f"Clip {clip['index']}: {clip['headline']}")
        print(f"  ⏱️  Duration: {clip['duration']:.1f}s")
        print(f"  📍 Timespan: {clip['start_time']:.1f}s - {clip['end_time']:.1f}s")
        print(f"  🎭 Appeal: {clip['emotional_appeal']}")
        print()


def main():
    """Main test function"""
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║                  PulsePoint AI                         ║
    ║         API Testing & Demonstration Script             ║
    ╚════════════════════════════════════════════════════════╝
    """)

    # Step 1: Health check
    if not test_health_check():
        print("\n⚠️  Warning: API keys not configured!")
        print("Please set OPENAI_API_KEY and GOOGLE_API_KEY in .env file")
        return

    # Step 2: Choose input method
    print("\n\nChoose input method:")
    print("1. Upload video file")
    print("2. Process from URL")
    print("3. Use test sample (if available)")

    choice = input("\nEnter choice (1-3): ").strip()

    job_id = None

    if choice == '1':
        video_path = input("Enter path to video file: ").strip()
        job_id = upload_video(video_path)

    elif choice == '2':
        video_url = input("Enter video URL: ").strip()
        job_id = process_video_url(video_url)

    elif choice == '3':
        # Try to use sample video
        sample_path = "sample_video.mp4"
        if Path(sample_path).exists():
            job_id = upload_video(sample_path)
        else:
            print(f"❌ Sample video not found at {sample_path}")
            return

    else:
        print("Invalid choice")
        return

    if not job_id:
        print("\n❌ Failed to start processing")
        return

    # Step 3: Monitor progress
    result = monitor_job_status(job_id)

    if not result:
        return

    # Step 4: Display results
    display_results(result)

    # Step 5: Download clips
    if result.get('clips'):
        download = input("\nDownload clips? (y/n): ").strip().lower()
        if download == 'y':
            download_clips(job_id, result['clips'])

    print("\n" + "=" * 60)
    print("  Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
