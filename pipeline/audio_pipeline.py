"""
Audio Pipeline
- AssemblyAI for speech-to-text (if API key provided)
- Fallback: manual transcript input
- Then: transcript_analysis.py for scoring
NOTE: No raw acoustic model. Audio → text → analysis only.
"""

import os
import sys
import tempfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def transcribe_with_assemblyai(audio_file, api_key):
    """
    Transcribe audio using AssemblyAI API.

    Args:
        audio_file: File-like object
        api_key (str): AssemblyAI API key

    Returns:
        str: Transcript text or None on failure
    """
    tmp_path = None
    try:
        import assemblyai as aai
        aai.settings.api_key = api_key

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file.read())
            tmp_path = tmp.name

        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(tmp_path)

        if transcript.status == aai.TranscriptStatus.error:
            return None
        return transcript.text

    except Exception as e:
        print(f"AssemblyAI error: {e}")
        return None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def analyze_audio(audio_file=None, manual_transcript=None, api_key=None):
    """
    Full audio analysis pipeline.

    Returns:
        dict: Audio/text analysis result.
    """
    from modules.transcript_analysis import analyze_transcript

    transcript = None

    if audio_file is not None and api_key:
        transcript = transcribe_with_assemblyai(audio_file, api_key)

    if not transcript and manual_transcript:
        transcript = manual_transcript.strip()

    if not transcript:
        return {
            "audio_text_score": 0.0,
            "transcript": "",
            "echolalia_score": 0.0,
            "pronoun_reversal": 0.0,
            "repetition_score": 0.0,
            "word_count": 0,
            "unique_words": 0,
            "vocabulary_ratio": 0.0,
            "error": "No transcript available"
        }

    return analyze_transcript(transcript)
