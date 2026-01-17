"""Transcription service using AssemblyAI"""
import logging
from pathlib import Path
from typing import List, Dict
import time
import requests
import urllib3

# Disable SSL warnings (for development only)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Handles video transcription using AssemblyAI (Free tier: 100 hours/month)"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.assemblyai.com/v2"
        self.headers = {
            "authorization": api_key,
            "content-type": "application/json"
        }

    def transcribe_video(self, audio_path: str) -> Dict:
        """
        Transcribe video audio to text with timestamps using AssemblyAI

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with transcription and segments
        """
        logger.info(f"Transcribing audio from {audio_path}")

        try:
            # Step 1: Upload audio file
            logger.info("Uploading audio file to AssemblyAI...")
            upload_url = self._upload_file(audio_path)

            # Step 2: Request transcription
            logger.info("Requesting transcription...")
            transcript_id = self._request_transcription(upload_url)

            # Step 3: Poll for completion
            logger.info("Waiting for transcription to complete...")
            transcript_data = self._poll_transcription(transcript_id)

            # Step 4: Extract segments
            segments = []
            if transcript_data.get('words'):
                # Group words into sentences/segments
                segments = self._create_segments_from_words(transcript_data['words'])

            result = {
                'text': transcript_data.get('text', ''),
                'segments': segments,
                'language': transcript_data.get('language_code', 'en')
            }

            logger.info(f"Transcription complete: {len(segments)} segments")
            return result

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            # Return empty result if transcription fails
            return {
                'text': '',
                'segments': [],
                'language': 'en'
            }

    def _upload_file(self, audio_path: str) -> str:
        """Upload audio file to AssemblyAI"""
        upload_endpoint = f"{self.base_url}/upload"

        with open(audio_path, 'rb') as f:
            response = requests.post(
                upload_endpoint,
                headers={"authorization": self.api_key},
                data=f,
                verify=False  # Disable SSL verification for development
            )

        if response.status_code != 200:
            raise Exception(f"Upload failed: {response.text}")

        return response.json()['upload_url']

    def _request_transcription(self, audio_url: str) -> str:
        """Request transcription from AssemblyAI"""
        transcript_endpoint = f"{self.base_url}/transcript"

        json_data = {
            "audio_url": audio_url,
            "language_detection": True,
            "punctuate": True,
            "format_text": True
        }

        response = requests.post(
            transcript_endpoint,
            json=json_data,
            headers=self.headers,
            verify=False  # Disable SSL verification for development
        )

        if response.status_code != 200:
            raise Exception(f"Transcription request failed: {response.text}")

        return response.json()['id']

    def _poll_transcription(self, transcript_id: str, max_wait: int = 600) -> Dict:
        """Poll for transcription completion"""
        polling_endpoint = f"{self.base_url}/transcript/{transcript_id}"

        start_time = time.time()

        while time.time() - start_time < max_wait:
            response = requests.get(polling_endpoint, headers=self.headers, verify=False)

            if response.status_code != 200:
                raise Exception(f"Polling failed: {response.text}")

            data = response.json()
            status = data['status']

            if status == 'completed':
                return data
            elif status == 'error':
                raise Exception(f"Transcription error: {data.get('error', 'Unknown error')}")

            # Wait before polling again
            time.sleep(3)

        raise Exception("Transcription timeout")

    def _create_segments_from_words(self, words: List[Dict]) -> List[Dict]:
        """Create sentence-like segments from word-level timestamps"""
        if not words:
            return []

        segments = []
        current_segment = {
            'start': words[0]['start'] / 1000.0,  # Convert ms to seconds
            'text': '',
            'words': []
        }

        for word in words:
            word_text = word['text']
            current_segment['words'].append(word_text)
            current_segment['text'] += word_text + ' '

            # End segment on punctuation or after ~10 words
            if (word_text.endswith(('.', '!', '?')) or
                len(current_segment['words']) >= 10):

                current_segment['end'] = word['end'] / 1000.0
                current_segment['text'] = current_segment['text'].strip()

                segments.append({
                    'start': current_segment['start'],
                    'end': current_segment['end'],
                    'text': current_segment['text']
                })

                # Start new segment
                if word != words[-1]:
                    next_word = words[words.index(word) + 1]
                    current_segment = {
                        'start': next_word['start'] / 1000.0,
                        'text': '',
                        'words': []
                    }

        # Add final segment if it has content
        if current_segment['words']:
            current_segment['end'] = words[-1]['end'] / 1000.0
            current_segment['text'] = current_segment['text'].strip()
            segments.append({
                'start': current_segment['start'],
                'end': current_segment['end'],
                'text': current_segment['text']
            })

        return segments

    def get_segment_at_time(self, segments: List[Dict], timestamp: float,
                           context_window: int = 3) -> str:
        """
        Get text segment at a specific timestamp with context

        Args:
            segments: List of transcription segments
            timestamp: Target timestamp in seconds
            context_window: Number of sentences before/after to include

        Returns:
            Text content around the timestamp
        """
        # Find segment containing timestamp
        target_idx = None
        for i, segment in enumerate(segments):
            if segment['start'] <= timestamp <= segment['end']:
                target_idx = i
                break

        if target_idx is None:
            # Find closest segment
            target_idx = min(
                range(len(segments)),
                key=lambda i: abs(segments[i]['start'] - timestamp)
            )

        # Get context window
        start_idx = max(0, target_idx - context_window)
        end_idx = min(len(segments), target_idx + context_window + 1)

        context_segments = segments[start_idx:end_idx]
        return ' '.join(seg['text'] for seg in context_segments)

    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text using GPT

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment analysis
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a sentiment analyzer. Analyze the emotional tone and engagement level of the text. Respond with a JSON object containing 'sentiment' (positive/negative/neutral), 'engagement_score' (0-10), and 'emotional_intensity' (low/medium/high)."},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=150
            )

            # Parse response
            content = response.choices[0].message.content

            # Simple parsing (you might want to use json.loads for production)
            sentiment_data = {
                'sentiment': 'neutral',
                'engagement_score': 5,
                'emotional_intensity': 'medium',
                'raw_analysis': content
            }

            return sentiment_data

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                'sentiment': 'neutral',
                'engagement_score': 5,
                'emotional_intensity': 'medium'
            }
