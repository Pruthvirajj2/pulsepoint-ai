"""Audio analysis for detecting emotional peaks and high-energy moments"""
import librosa
import numpy as np
from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """Analyzes audio to detect emotional peaks and high-energy moments"""

    def __init__(self, audio_path: str):
        self.audio_path = audio_path
        self.y, self.sr = librosa.load(audio_path, sr=None)
        self.duration = librosa.get_duration(y=self.y, sr=self.sr)

    def analyze_energy(self, window_size: int = 5) -> np.ndarray:
        """
        Analyze audio energy over time

        Args:
            window_size: Size of the analysis window in seconds

        Returns:
            Array of energy values over time
        """
        # Calculate RMS energy
        hop_length = 512
        rms = librosa.feature.rms(y=self.y, hop_length=hop_length)[0]

        # Convert to time-based representation
        times = librosa.frames_to_time(np.arange(len(rms)), sr=self.sr, hop_length=hop_length)

        return times, rms

    def detect_volume_spikes(self, percentile: float = 85) -> List[float]:
        """
        Detect moments with high volume/energy

        Args:
            percentile: Percentile threshold for spike detection

        Returns:
            List of timestamps with volume spikes
        """
        times, rms = self.analyze_energy()

        # Find peaks above threshold
        threshold = np.percentile(rms, percentile)
        spike_indices = np.where(rms > threshold)[0]

        # Group nearby spikes
        spike_times = []
        if len(spike_indices) > 0:
            current_group = [times[spike_indices[0]]]

            for i in range(1, len(spike_indices)):
                if spike_indices[i] - spike_indices[i-1] > 10:  # New group
                    spike_times.append(np.mean(current_group))
                    current_group = [times[spike_indices[i]]]
                else:
                    current_group.append(times[spike_indices[i]])

            # Add last group
            if current_group:
                spike_times.append(np.mean(current_group))

        logger.info(f"Detected {len(spike_times)} volume spikes")
        return spike_times

    def analyze_pitch_variation(self) -> List[float]:
        """
        Detect moments with significant pitch variation (excitement, emphasis)

        Returns:
            List of timestamps with high pitch variation
        """
        # Extract pitch using piptrack
        pitches, magnitudes = librosa.piptrack(y=self.y, sr=self.sr)

        # Get the pitch with highest magnitude at each frame
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            pitch_values.append(pitch if pitch > 0 else 0)

        pitch_values = np.array(pitch_values)

        # Calculate pitch variation over sliding window
        window = 20
        pitch_variation = np.convolve(
            np.abs(np.diff(pitch_values)),
            np.ones(window)/window,
            mode='same'
        )

        # Find high variation moments
        threshold = np.percentile(pitch_variation, 80)
        high_var_indices = np.where(pitch_variation > threshold)[0]

        hop_length = 512
        times = librosa.frames_to_time(high_var_indices, sr=self.sr, hop_length=hop_length)

        # Group nearby moments
        grouped_times = []
        if len(times) > 0:
            current_group = [times[0]]

            for i in range(1, len(times)):
                if times[i] - times[i-1] > 5:  # New group (5 second gap)
                    grouped_times.append(np.mean(current_group))
                    current_group = [times[i]]
                else:
                    current_group.append(times[i])

            if current_group:
                grouped_times.append(np.mean(current_group))

        logger.info(f"Detected {len(grouped_times)} pitch variation moments")
        return grouped_times

    def detect_silence_periods(self, threshold_db: float = -40) -> List[Tuple[float, float]]:
        """
        Detect silence periods to help segment the audio

        Args:
            threshold_db: Silence threshold in dB

        Returns:
            List of (start, end) tuples for silence periods
        """
        # Convert to dB
        db = librosa.amplitude_to_db(np.abs(self.y), ref=np.max)

        # Find silent frames
        silent = db < threshold_db

        # Find boundaries
        boundaries = np.diff(silent.astype(int))
        silence_starts = np.where(boundaries == 1)[0]
        silence_ends = np.where(boundaries == -1)[0]

        # Convert to time
        silence_periods = []
        for start, end in zip(silence_starts, silence_ends):
            start_time = librosa.samples_to_time(start, sr=self.sr)
            end_time = librosa.samples_to_time(end, sr=self.sr)

            # Only include silences longer than 1 second
            if end_time - start_time > 1.0:
                silence_periods.append((start_time, end_time))

        return silence_periods

    def get_emotional_peaks(self, num_peaks: int = 10) -> List[Dict]:
        """
        Combine multiple analysis methods to find emotional peaks
        distributed across the video duration

        Args:
            num_peaks: Maximum number of peaks to return

        Returns:
            List of peak information dictionaries
        """
        # Get volume spikes
        volume_spikes = self.detect_volume_spikes()

        # Get pitch variation moments
        pitch_moments = self.analyze_pitch_variation()

        # Get energy timeline
        times, rms = self.analyze_energy()

        # Combine and score all moments
        all_moments = {}

        # Add volume spikes with high score
        for spike_time in volume_spikes:
            all_moments[spike_time] = all_moments.get(spike_time, 0) + 2.0

        # Add pitch variation moments
        for pitch_time in pitch_moments:
            all_moments[pitch_time] = all_moments.get(pitch_time, 0) + 1.5

        # For longer videos, ensure distribution across duration
        if self.duration > 120:  # If video is longer than 2 minutes
            # Divide video into segments
            num_segments = min(num_peaks, int(self.duration / 60))  # 1 segment per minute
            segment_duration = self.duration / num_segments

            # Get best peak from each segment
            distributed_moments = []
            for seg_idx in range(num_segments):
                seg_start = seg_idx * segment_duration
                seg_end = (seg_idx + 1) * segment_duration

                # Find moments in this segment
                segment_moments = {t: s for t, s in all_moments.items()
                                 if seg_start <= t < seg_end}

                if segment_moments:
                    # Get best moment from segment
                    best_moment = max(segment_moments.items(), key=lambda x: x[1])
                    distributed_moments.append(best_moment)
                else:
                    # No peaks in segment, find highest energy point
                    seg_times_mask = (times >= seg_start) & (times < seg_end)
                    if np.any(seg_times_mask):
                        seg_energies = rms[seg_times_mask]
                        seg_times_filtered = times[seg_times_mask]
                        if len(seg_energies) > 0:
                            max_energy_idx = np.argmax(seg_energies)
                            timestamp = float(seg_times_filtered[max_energy_idx])
                            distributed_moments.append((timestamp, 1.0))

            top_moments = distributed_moments
        else:
            # For shorter videos, use top moments as before
            sorted_moments = sorted(all_moments.items(), key=lambda x: x[1], reverse=True)
            top_moments = sorted_moments[:num_peaks]

        # Create result with additional context
        peaks = []
        for timestamp, score in top_moments:
            # Find nearest energy value
            nearest_idx = np.argmin(np.abs(times - timestamp))
            energy = float(rms[nearest_idx])

            peaks.append({
                'timestamp': float(timestamp),
                'score': float(score),
                'energy': energy,
                'reason': self._get_peak_reason(timestamp, volume_spikes, pitch_moments)
            })

        # Sort by timestamp
        peaks.sort(key=lambda x: x['timestamp'])

        logger.info(f"Identified {len(peaks)} emotional peaks")
        return peaks

    def _get_peak_reason(self, timestamp: float, volume_spikes: List[float],
                        pitch_moments: List[float]) -> str:
        """Get reason for peak detection"""
        reasons = []

        # Check if it's a volume spike
        if any(abs(spike - timestamp) < 2 for spike in volume_spikes):
            reasons.append("high energy")

        # Check if it's a pitch variation moment
        if any(abs(moment - timestamp) < 2 for moment in pitch_moments):
            reasons.append("emphasis")

        return " + ".join(reasons) if reasons else "notable moment"
