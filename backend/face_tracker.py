"""Face tracking for smart crop to vertical format"""
import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class FaceTracker:
    """Tracks faces in video to enable smart cropping"""

    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 1 for far-range detection
            min_detection_confidence=0.5
        )

    def detect_faces_in_frame(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in a single frame

        Args:
            frame: Video frame (BGR format)

        Returns:
            List of bounding boxes (x, y, width, height)
        """
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        results = self.face_detection.process(rgb_frame)

        faces = []
        if results.detections:
            h, w, _ = frame.shape

            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box

                # Convert relative coordinates to absolute
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)

                faces.append((x, y, width, height))

        return faces

    def track_face_in_video(self, video_path: str,
                           start_time: float,
                           duration: float,
                           sample_rate: int = 5) -> List[Tuple[int, int]]:
        """
        Track face position throughout a video clip

        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            duration: Duration in seconds
            sample_rate: Sample every N frames

        Returns:
            List of (center_x, center_y) positions
        """
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            logger.error(f"Failed to open video: {video_path}")
            return []

        fps = cap.get(cv2.CAP_PROP_FPS)
        start_frame = int(start_time * fps)
        end_frame = int((start_time + duration) * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        face_positions = []
        frame_count = start_frame

        while frame_count < end_frame:
            ret, frame = cap.read()

            if not ret:
                break

            # Sample frames
            if (frame_count - start_frame) % sample_rate == 0:
                faces = self.detect_faces_in_frame(frame)

                if faces:
                    # Use the largest face
                    largest_face = max(faces, key=lambda f: f[2] * f[3])
                    x, y, w, h = largest_face

                    # Calculate center
                    center_x = x + w // 2
                    center_y = y + h // 2

                    face_positions.append((center_x, center_y))

            frame_count += 1

        cap.release()

        logger.info(f"Tracked face in {len(face_positions)} frames")
        return face_positions

    def calculate_smart_crop(self, video_path: str,
                            start_time: float,
                            duration: float,
                            target_aspect: Tuple[int, int] = (9, 16)) -> Tuple[int, int, int, int]:
        """
        Calculate optimal crop region to keep face centered in vertical format

        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            duration: Duration in seconds
            target_aspect: Target aspect ratio (width, height)

        Returns:
            Crop region (x, y, width, height)
        """
        # Track face positions
        face_positions = self.track_face_in_video(video_path, start_time, duration)

        # Get video dimensions
        cap = cv2.VideoCapture(video_path)
        video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()

        if not face_positions:
            # Fallback: center crop
            logger.warning("No faces detected, using center crop")
            return self._center_crop(video_width, video_height, target_aspect)

        # Calculate average face position with smoothing
        avg_x = int(np.median([pos[0] for pos in face_positions]))
        avg_y = int(np.median([pos[1] for pos in face_positions]))

        # Calculate crop dimensions
        target_w, target_h = target_aspect
        aspect_ratio = target_w / target_h

        # Determine crop size based on video height
        crop_height = video_height
        crop_width = int(crop_height * aspect_ratio)

        # If crop is wider than video, use video width
        if crop_width > video_width:
            crop_width = video_width
            crop_height = int(crop_width / aspect_ratio)

        # Center crop on face position
        crop_x = max(0, min(avg_x - crop_width // 2, video_width - crop_width))
        crop_y = max(0, min(avg_y - crop_height // 2, video_height - crop_height))

        # Adjust to keep face in upper-middle region (looks better for talking head)
        crop_y = max(0, min(crop_y, video_height - crop_height))

        logger.info(f"Smart crop calculated: ({crop_x}, {crop_y}, {crop_width}, {crop_height})")
        return (crop_x, crop_y, crop_width, crop_height)

    def _center_crop(self, video_width: int, video_height: int,
                    target_aspect: Tuple[int, int]) -> Tuple[int, int, int, int]:
        """Calculate center crop when face detection fails"""

        target_w, target_h = target_aspect
        aspect_ratio = target_w / target_h

        # Use video height
        crop_height = video_height
        crop_width = int(crop_height * aspect_ratio)

        if crop_width > video_width:
            crop_width = video_width
            crop_height = int(crop_width / aspect_ratio)

        crop_x = (video_width - crop_width) // 2
        crop_y = (video_height - crop_height) // 2

        return (crop_x, crop_y, crop_width, crop_height)

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'face_detection'):
            self.face_detection.close()
