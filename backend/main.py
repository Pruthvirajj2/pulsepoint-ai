"""FastAPI application for PulsePoint AI"""
import logging
import uuid
from pathlib import Path
from typing import Optional
import shutil

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from .config import get_settings, ensure_directories
from .video_processor import VideoProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PulsePoint AI",
    description="Transform long-form videos into viral short-form content",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Settings
settings = get_settings()

# Ensure directories exist
ensure_directories()

# Job status storage (in production, use Redis or database)
job_status = {}


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("PulsePoint AI starting up...")

    # Mount static files
    if settings.output_dir.exists():
        app.mount("/outputs", StaticFiles(directory=str(settings.output_dir)), name="outputs")

    logger.info("Startup complete")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to PulsePoint AI",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api_keys_configured": {
            "assemblyai": bool(settings.assemblyai_api_key),
            "google": bool(settings.google_api_key)
        }
    }


@app.post("/api/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload a video for processing

    Args:
        file: Video file

    Returns:
        Job information
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(
            status_code=400,
            detail="File must be a video"
        )

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Save uploaded file
    file_extension = Path(file.filename).suffix
    upload_path = settings.upload_dir / f"{job_id}{file_extension}"

    try:
        with open(upload_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Video uploaded: {upload_path}")

        # Initialize job status
        job_status[job_id] = {
            'job_id': job_id,
            'status': 'queued',
            'progress': 0,
            'message': 'Video uploaded, processing queued'
        }

        # Start processing in background
        background_tasks.add_task(
            process_video_background,
            str(upload_path),
            job_id
        )

        return JSONResponse({
            'success': True,
            'job_id': job_id,
            'message': 'Video uploaded successfully. Processing started.'
        })

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@app.post("/api/process-url")
async def process_video_url(
    background_tasks: BackgroundTasks,
    video_url: str
):
    """
    Process a video from URL (e.g., Google Drive)

    Args:
        video_url: URL to video file

    Returns:
        Job information
    """
    # Generate job ID
    job_id = str(uuid.uuid4())

    # For Google Drive, convert to direct download link
    if 'drive.google.com' in video_url:
        video_url = convert_google_drive_url(video_url)

    # Initialize job status
    job_status[job_id] = {
        'job_id': job_id,
        'status': 'queued',
        'progress': 0,
        'message': 'Downloading video from URL'
    }

    # Download and process in background
    background_tasks.add_task(
        download_and_process_video,
        video_url,
        job_id
    )

    return JSONResponse({
        'success': True,
        'job_id': job_id,
        'message': 'Processing started. Check status for updates.'
    })


@app.get("/api/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get job status

    Args:
        job_id: Job identifier

    Returns:
        Job status information
    """
    if job_id not in job_status:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job_status[job_id]


@app.get("/api/download/{job_id}/{clip_index}")
async def download_clip(job_id: str, clip_index: int, request: Request):
    """
    Download/stream a specific clip with Range support for video playback

    Args:
        job_id: Job identifier
        clip_index: Clip index (1-based)
        request: HTTP request (for Range header)

    Returns:
        Video file with streaming support
    """
    filename = f"{job_id}_clip_{clip_index}.mp4"
    file_path = settings.output_dir / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Clip not found"
        )

    # Get file size
    file_size = os.path.getsize(file_path)

    # Check for Range header
    range_header = request.headers.get("range")

    if range_header:
        # Parse range header (format: "bytes=start-end")
        byte_range = range_header.replace("bytes=", "").split("-")
        start = int(byte_range[0]) if byte_range[0] else 0
        end = int(byte_range[1]) if len(byte_range) > 1 and byte_range[1] else file_size - 1

        # Ensure valid range
        start = max(0, start)
        end = min(end, file_size - 1)
        content_length = end - start + 1

        # Open file and seek to start position
        def iterfile():
            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = content_length
                while remaining > 0:
                    chunk_size = min(8192, remaining)
                    data = f.read(chunk_size)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data

        # Return partial content with 206 status
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": "video/mp4",
        }

        return StreamingResponse(
            iterfile(),
            status_code=206,
            headers=headers,
            media_type="video/mp4"
        )

    else:
        # No range header - return full file
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
            "Content-Type": "video/mp4",
        }

        return FileResponse(
            path=str(file_path),
            media_type='video/mp4',
            filename=filename,
            headers=headers
        )


def convert_google_drive_url(url: str) -> str:
    """Convert Google Drive share URL to direct download URL"""
    if '/file/d/' in url:
        file_id = url.split('/file/d/')[1].split('/')[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return url


async def download_and_process_video(video_url: str, job_id: str):
    """Download video from URL and process it"""
    import requests

    try:
        job_status[job_id]['status'] = 'downloading'
        job_status[job_id]['message'] = 'Downloading video...'

        # Download video
        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        # Save to file
        video_path = settings.upload_dir / f"{job_id}.mp4"
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Video downloaded: {video_path}")

        # Process video
        await process_video_background(str(video_path), job_id)

    except Exception as e:
        logger.error(f"Download failed: {e}")
        job_status[job_id]['status'] = 'failed'
        job_status[job_id]['message'] = f'Download failed: {str(e)}'


async def process_video_background(video_path: str, job_id: str):
    """Background task to process video"""
    try:
        job_status[job_id]['status'] = 'processing'
        job_status[job_id]['progress'] = 10
        job_status[job_id]['message'] = 'Initializing video processing...'

        # Check API keys
        if not settings.assemblyai_api_key or not settings.google_api_key:
            raise ValueError("API keys not configured. Please set ASSEMBLYAI_API_KEY and GOOGLE_API_KEY in .env file")

        # Initialize processor
        processor = VideoProcessor(
            assemblyai_api_key=settings.assemblyai_api_key,
            google_api_key=settings.google_api_key
        )

        job_status[job_id]['progress'] = 20
        job_status[job_id]['message'] = 'Analyzing video content...'

        # Process video
        result = processor.process_video(video_path, job_id)

        if result['success']:
            job_status[job_id]['status'] = 'completed'
            job_status[job_id]['progress'] = 100
            job_status[job_id]['message'] = 'Processing complete!'
            job_status[job_id]['clips'] = result['clips']
            job_status[job_id]['metadata_path'] = result['metadata_path']

            logger.info(f"Job {job_id} completed successfully")
        else:
            raise Exception(result.get('error', 'Unknown error'))

    except Exception as e:
        logger.error(f"Processing failed for job {job_id}: {e}", exc_info=True)
        job_status[job_id]['status'] = 'failed'
        job_status[job_id]['message'] = f'Processing failed: {str(e)}'


def start_server():
    """Start the FastAPI server"""
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )


if __name__ == "__main__":
    start_server()
