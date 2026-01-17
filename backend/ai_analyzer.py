"""AI-powered content analysis using Google Gemini"""
import logging
from typing import List, Dict
import google.generativeai as genai
import json

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Uses Gemini to identify the best moments in video content"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Use the correct model name for Gemini API
        try:
            self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        except:
            # Fallback to basic model if pro not available
            self.model = genai.GenerativeModel('models/gemini-pro')

    def analyze_transcript_for_moments(self, transcript: str,
                                      segments: List[Dict],
                                      num_clips: int = 5) -> List[Dict]:
        """
        Analyze full transcript to identify the best moments for short clips

        Args:
            transcript: Full transcript text
            segments: Transcript segments with timestamps
            num_clips: Number of clips to identify

        Returns:
            List of identified moments with metadata
        """
        logger.info("Analyzing transcript with Gemini AI")

        # Create prompt for Gemini
        prompt = f"""You are an expert content strategist specializing in creating viral short-form video content from long-form videos.

Analyze this video transcript and identify the {num_clips} BEST moments that would make engaging 30-60 second clips for TikTok, Instagram Reels, or YouTube Shorts.

For each moment, provide:
1. A catchy headline/hook (max 8 words) that would stop someone from scrolling
2. The key message or insight
3. Why this moment has viral potential
4. The approximate timestamp or key phrase from the transcript to help locate it
5. Emotional appeal (inspiration/humor/shock/education/etc.)

Transcript:
{transcript[:50000]}

Respond with a JSON array of objects with these fields: headline, key_message, viral_potential, search_phrase, emotional_appeal, estimated_duration

Be specific and actionable. Focus on moments with:
- Strong emotional hooks
- Quotable insights
- Surprising revelations
- Practical wisdom
- Passionate delivery
"""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text

            # Try to extract JSON from response
            moments = self._parse_gemini_response(result_text, segments)

            logger.info(f"Gemini identified {len(moments)} key moments")
            return moments

        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            # Fallback: return evenly spaced moments
            return self._create_fallback_moments(segments, num_clips)

    def _parse_gemini_response(self, response_text: str,
                               segments: List[Dict]) -> List[Dict]:
        """Parse Gemini's response and match to timestamps"""

        moments = []

        try:
            # Try to find JSON in response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed_moments = json.loads(json_str)

                # Match each moment to a timestamp
                for moment in parsed_moments:
                    search_phrase = moment.get('search_phrase', '')

                    # Find matching segment
                    timestamp = self._find_timestamp_for_phrase(
                        search_phrase,
                        segments
                    )

                    moments.append({
                        'headline': moment.get('headline', 'Key Moment'),
                        'key_message': moment.get('key_message', ''),
                        'viral_potential': moment.get('viral_potential', ''),
                        'emotional_appeal': moment.get('emotional_appeal', 'educational'),
                        'timestamp': timestamp,
                        'estimated_duration': moment.get('estimated_duration', 45),
                        'ai_selected': True
                    })

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from Gemini: {e}")
            # Fall back to text parsing
            moments = self._parse_text_response(response_text, segments)

        return moments

    def _parse_text_response(self, response_text: str,
                            segments: List[Dict]) -> List[Dict]:
        """Parse text response if JSON parsing fails"""
        moments = []
        lines = response_text.split('\n')

        current_moment = {}
        for line in lines:
            line = line.strip()

            if 'headline' in line.lower() or 'hook' in line.lower():
                if current_moment:
                    moments.append(current_moment)
                current_moment = {'headline': line.split(':', 1)[-1].strip()}

            elif 'message' in line.lower():
                current_moment['key_message'] = line.split(':', 1)[-1].strip()

            elif 'phrase' in line.lower() or 'timestamp' in line.lower():
                phrase = line.split(':', 1)[-1].strip()
                current_moment['search_phrase'] = phrase
                current_moment['timestamp'] = self._find_timestamp_for_phrase(
                    phrase, segments
                )

        if current_moment and 'timestamp' in current_moment:
            moments.append(current_moment)

        return moments

    def _find_timestamp_for_phrase(self, search_phrase: str,
                                   segments: List[Dict]) -> float:
        """Find timestamp for a given phrase in segments"""

        search_lower = search_phrase.lower()

        # Search for phrase in segments
        for segment in segments:
            if search_lower in segment['text'].lower():
                # Return middle of segment
                return (segment['start'] + segment['end']) / 2

        # If not found, return a random-ish timestamp
        # based on hash of phrase
        if segments:
            idx = hash(search_phrase) % len(segments)
            return segments[idx]['start']

        return 0.0

    def _create_fallback_moments(self, segments: List[Dict],
                                num_clips: int) -> List[Dict]:
        """Create fallback moments if AI analysis fails"""

        if not segments:
            return []

        total_duration = segments[-1]['end'] if segments else 0
        interval = total_duration / (num_clips + 1)

        moments = []
        for i in range(num_clips):
            timestamp = interval * (i + 1)

            moments.append({
                'headline': f'Key Moment {i+1}',
                'key_message': 'Important insight from this section',
                'viral_potential': 'Educational content',
                'emotional_appeal': 'informative',
                'timestamp': timestamp,
                'estimated_duration': 45,
                'ai_selected': False
            })

        return moments

    def generate_caption(self, text: str, style: str = "engaging") -> str:
        """
        Generate an engaging caption for a clip

        Args:
            text: Content of the clip
            style: Caption style (engaging, professional, humorous)

        Returns:
            Generated caption
        """
        prompt = f"""Create a short, {style} caption for this video clip excerpt.
The caption should be attention-grabbing and make people want to watch.
Max 15 words.

Clip content: {text[:500]}

Respond with just the caption, no quotes or extra text."""

        try:
            response = self.model.generate_content(prompt)
            caption = response.text.strip().strip('"\'')
            return caption

        except Exception as e:
            logger.error(f"Caption generation failed: {e}")
            # Fallback to first sentence
            first_sentence = text.split('.')[0]
            return first_sentence[:80] + "..." if len(first_sentence) > 80 else first_sentence
