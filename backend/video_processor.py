"""Main video processing orchestrator"""
import logging
from pathlib import Path
from typing import List, Dict, Optional
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.fx import crop, resize
import json

from .audio_analyzer import AudioAnalyzer
from .transcription_service import TranscriptionService
from .ai_analyzer import AIAnalyzer
from .face_tracker import FaceTracker
from .config import get_settings

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Orchestrates the entire video processing pipeline"""

    def __init__(self, assemblyai_api_key: str, google_api_key: str):
        self.settings = get_settings()
        self.transcription_service = TranscriptionService(assemblyai_api_key)
        self.ai_analyzer = AIAnalyzer(google_api_key)
        self.face_tracker = FaceTracker()

    def process_video(self, video_path: str, job_id: str) -> Dict:
        """
        Process a video to extract viral clips

        Args:
            video_path: Path to input video
            job_id: Unique job identifier

        Returns:
            Dictionary with processing results
        """
        logger.info(f"Starting video processing for job {job_id}")

        try:
            # Step 1: Extract audio for analysis
            logger.info("Step 1: Extracting audio")
            audio_path = self._extract_audio(video_path, job_id)

            # Step 2: Analyze audio for emotional peaks
            logger.info("Step 2: Analyzing audio for emotional peaks")
            audio_analyzer = AudioAnalyzer(audio_path)
            emotional_peaks = audio_analyzer.get_emotional_peaks(num_peaks=15)

            # Step 3: Transcribe audio (with fallback)
            logger.info("Step 3: Transcribing audio")
            try:
                transcription = self.transcription_service.transcribe_video(audio_path)
            except Exception as e:
                logger.warning(f"Transcription failed: {e}. Continuing with audio-only analysis.")
                transcription = {
                    'text': '',
                    'segments': [],
                    'language': 'unknown'
                }

            # Step 4: Use AI to identify best moments (with fallback)
            logger.info("Step 4: Using AI to identify best moments")
            try:
                ai_moments = self.ai_analyzer.analyze_transcript_for_moments(
                    transcription['text'],
                    transcription['segments'],
                    num_clips=self.settings.max_clips
                )
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}. Using audio peaks only.")
                ai_moments = []

            # Step 5: Combine audio peaks with AI insights
            logger.info("Step 5: Combining insights to select final clips")
            selected_moments = self._select_best_moments(
                emotional_peaks,
                ai_moments,
                transcription['segments']
            )

            # Step 6: Create clips
            logger.info("Step 6: Creating video clips")
            clips = self._create_clips(
                video_path,
                selected_moments,
                transcription['segments'],
                job_id
            )

            # Step 7: Save metadata
            metadata = {
                'job_id': job_id,
                'original_video': video_path,
                'emotional_peaks': emotional_peaks,
                'ai_moments': ai_moments,
                'selected_moments': selected_moments,
                'clips': clips,
                'transcription_summary': {
                    'total_segments': len(transcription['segments']),
                    'language': transcription['language']
                }
            }

            metadata_path = self.settings.output_dir / f"{job_id}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Processing complete: {len(clips)} clips created")

            return {
                'success': True,
                'job_id': job_id,
                'clips': clips,
                'metadata_path': str(metadata_path)
            }

        except Exception as e:
            logger.error(f"Video processing failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'job_id': job_id
            }

    def _extract_audio(self, video_path: str, job_id: str) -> str:
        """Extract audio from video"""
        video = VideoFileClip(video_path)
        audio_path = str(self.settings.temp_dir / f"{job_id}_audio.wav")

        video.audio.write_audiofile(audio_path, logger=None)
        video.close()

        return audio_path

    def _select_best_moments(self, emotional_peaks: List[Dict],
                            ai_moments: List[Dict],
                            segments: List[Dict]) -> List[Dict]:
        """
        Combine audio analysis and AI insights to select final moments

        Args:
            emotional_peaks: Audio analysis results
            ai_moments: AI-identified moments
            segments: Transcription segments

        Returns:
            List of selected moments with complete metadata
        """
        # Always use emotional peaks as the base (guaranteed to have moments)
        # Sort peaks by score to get the best ones
        sorted_peaks = sorted(emotional_peaks, key=lambda x: x['score'], reverse=True)

        selected_moments = []

        # Select peaks with good spacing (at least 30 seconds apart)
        for peak in sorted_peaks:
            if len(selected_moments) >= self.settings.max_clips:
                break

            peak_time = peak['timestamp']

            # Check spacing with already selected moments
            too_close = False
            for moment in selected_moments:
                if abs(moment['timestamp'] - peak_time) < 30:
                    too_close = True
                    break

            if not too_close:
                selected_moments.append({
                    'timestamp': peak_time,
                    'score': peak['score'],
                    'headline': 'Peak Moment',
                    'reason': f"Audio: {peak['reason']} (energy: {peak['energy']:.2f})",
                    'emotional_appeal': 'energetic',
                    'estimated_duration': 40,
                    'audio_peak': True
                })

        # If we still don't have enough clips, reduce spacing requirement
        if len(selected_moments) < self.settings.max_clips:
            logger.warning(f"Only {len(selected_moments)} moments with 30s spacing, reducing to 15s")

            for peak in sorted_peaks:
                if len(selected_moments) >= self.settings.max_clips:
                    break

                peak_time = peak['timestamp']

                # Check if already added
                already_added = any(abs(m['timestamp'] - peak_time) < 1 for m in selected_moments)
                if already_added:
                    continue

                # Check 15s spacing
                too_close = False
                for moment in selected_moments:
                    if abs(moment['timestamp'] - peak_time) < 15:
                        too_close = True
                        break

                if not too_close:
                    selected_moments.append({
                        'timestamp': peak_time,
                        'score': peak['score'],
                        'headline': 'Peak Moment',
                        'reason': f"Audio: {peak['reason']}",
                        'emotional_appeal': 'energetic',
                        'estimated_duration': 40,
                        'audio_peak': True
                    })

        # Boost scores for AI-identified moments if they align
        for moment in ai_moments:
            ai_time = moment['timestamp']
            for selected in selected_moments:
                if abs(selected['timestamp'] - ai_time) < 10:
                    selected['score'] += 5.0
                    selected['headline'] = moment.get('headline', selected['headline'])
                    selected['emotional_appeal'] = moment.get('emotional_appeal', selected['emotional_appeal'])
                    break

        # Sort by timestamp for sequential processing
        selected_moments.sort(key=lambda x: x['timestamp'])

        logger.info(f"Selected {len(selected_moments)} moments from {len(emotional_peaks)} peaks")
        for i, m in enumerate(selected_moments):
            logger.info(f"  Moment {i+1}: {m['timestamp']:.1f}s - {m['headline']}")

        return selected_moments

    def _create_clips(self, video_path: str, moments: List[Dict],
                     segments: List[Dict], job_id: str) -> List[Dict]:
        """
        Create video clips from selected moments

        Args:
            video_path: Path to source video
            moments: Selected moments
            segments: Transcription segments
            job_id: Job identifier

        Returns:
            List of created clip information
        """
        video = VideoFileClip(video_path)
        clips = []

        for i, moment in enumerate(moments):
            try:
                clip_info = self._create_single_clip(
                    video,
                    moment,
                    segments,
                    job_id,
                    i
                )
                clips.append(clip_info)

            except Exception as e:
                logger.error(f"Failed to create clip {i}: {e}")
                continue

        video.close()
        return clips

    def _create_single_clip(self, video: VideoFileClip, moment: Dict,
                           segments: List[Dict], job_id: str, clip_index: int) -> Dict:
        """Create a single clip with all enhancements"""

        timestamp = moment['timestamp']
        duration = min(
            moment.get('estimated_duration', 45),
            self.settings.max_clip_duration
        )

        # Ensure we don't exceed video duration
        start_time = max(0, timestamp - duration // 2)
        end_time = min(video.duration, start_time + duration)

        # Adjust start time if needed
        if end_time - start_time < self.settings.min_clip_duration:
            start_time = max(0, end_time - self.settings.min_clip_duration)

        logger.info(f"Creating clip {clip_index} from {start_time:.1f}s to {end_time:.1f}s")

        # Extract clip
        clip = video.subclip(start_time, end_time)

        # Apply smart crop to vertical format
        try:
            crop_region = self.face_tracker.calculate_smart_crop(
                video.filename,
                start_time,
                end_time - start_time,
                target_aspect=(9, 16)
            )

            x, y, w, h = crop_region
            clip = crop.crop(clip, x1=x, y1=y, width=w, height=h)

            # Resize to standard vertical format (1080x1920)
            clip = resize.resize(clip, height=1920)

        except Exception as e:
            logger.warning(f"Smart crop failed, using center crop: {e}")
            # Fallback to simple center crop
            clip = self._apply_center_crop(clip)

        # Add captions
        try:
            clip = self._add_captions(clip, moment, segments, start_time, end_time)
        except Exception as e:
            logger.warning(f"Failed to add captions: {e}")

        # Export clip
        output_filename = f"{job_id}_clip_{clip_index + 1}.mp4"
        output_path = self.settings.output_dir / output_filename

        clip.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=str(self.settings.temp_dir / f'temp_audio_{clip_index}.m4a'),
            remove_temp=True,
            logger=None
        )

        clip.close()

        return {
            'index': clip_index + 1,
            'filename': output_filename,
            'path': str(output_path),
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time,
            'headline': moment.get('headline', f'Clip {clip_index + 1}'),
            'emotional_appeal': moment.get('emotional_appeal', 'engaging')
        }

    def _apply_center_crop(self, clip: VideoFileClip) -> VideoFileClip:
        """Apply simple center crop to vertical format"""

        w, h = clip.size
        target_aspect = 9 / 16

        # Calculate crop dimensions
        crop_height = h
        crop_width = int(crop_height * target_aspect)

        if crop_width > w:
            crop_width = w
            crop_height = int(crop_width / target_aspect)

        x1 = (w - crop_width) // 2
        y1 = (h - crop_height) // 2

        return crop.crop(clip, x1=x1, y1=y1, width=crop_width, height=crop_height)

    def _add_captions(self, clip: VideoFileClip, moment: Dict,
                     segments: List[Dict], start_time: float,
                     end_time: float) -> VideoFileClip:
        """Add dynamic captions to clip"""

        # Get headline
        headline = moment.get('headline', 'Watch This!')

        # Create text clip for headline
        txt_clip = TextClip(
            headline,
            fontsize=60,
            color='white',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=3,
            method='caption',
            size=(clip.w * 0.9, None)
        )

        # Position at top
        txt_clip = txt_clip.set_position(('center', 100))
        txt_clip = txt_clip.set_duration(min(3, clip.duration))

        # Composite
        final_clip = CompositeVideoClip([clip, txt_clip])

        return final_clip
