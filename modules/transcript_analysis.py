"""
Transcript Analysis Module
Analyzes speech transcript for autism indicators:
- Echolalia
- Pronoun reversal
- Repetition
- Vocabulary stats
"""

import re
from collections import Counter


def analyze_transcript(text):
    """
    Analyze a speech transcript for autism-related linguistic markers.

    Args:
        text (str): Speech transcript

    Returns:
        dict: Scores and statistics
    """
    if not text or not text.strip():
        return {
            "audio_text_score": 0.0,
            "transcript": "",
            "echolalia_score": 0.0,
            "pronoun_reversal": 0.0,
            "repetition_score": 0.0,
            "word_count": 0,
            "unique_words": 0,
            "vocabulary_ratio": 0.0
        }

    text_clean = text.lower().strip()
    words = re.findall(r'\b\w+\b', text_clean)
    word_count = len(words)

    if word_count == 0:
        return {
            "audio_text_score": 0.0,
            "transcript": text,
            "echolalia_score": 0.0,
            "pronoun_reversal": 0.0,
            "repetition_score": 0.0,
            "word_count": 0,
            "unique_words": 0,
            "vocabulary_ratio": 0.0
        }

    echolalia_score = _calculate_echolalia(words)
    pronoun_reversal = _calculate_pronoun_reversal(text_clean)
    repetition_score = _calculate_repetition(words)

    unique_words = len(set(words))
    vocabulary_ratio = unique_words / word_count if word_count > 0 else 0.0

    audio_text_score = (
        0.4 * echolalia_score +
        0.3 * pronoun_reversal +
        0.3 * repetition_score
    )
    audio_text_score = min(1.0, audio_text_score)

    return {
        "audio_text_score": round(audio_text_score, 3),
        "transcript": text,
        "echolalia_score": round(echolalia_score, 3),
        "pronoun_reversal": round(pronoun_reversal, 3),
        "repetition_score": round(repetition_score, 3),
        "word_count": word_count,
        "unique_words": unique_words,
        "vocabulary_ratio": round(vocabulary_ratio, 3)
    }


def _calculate_echolalia(words):
    """Detects repeated 3-word sequences."""
    if len(words) < 6:
        return 0.0
    trigrams = [tuple(words[i:i+3]) for i in range(len(words)-2)]
    counts = Counter(trigrams)
    repeated = sum(v - 1 for v in counts.values() if v > 1)
    total = len(trigrams)
    return min(1.0, repeated / total) if total > 0 else 0.0


def _calculate_pronoun_reversal(text):
    """Detects you/me pronoun reversal patterns."""
    reversals = [
        r'\byou want\b', r'\byou are hungry\b',
        r'\byou need\b', r'\byou like\b',
        r'\bme is\b', r'\bme want\b'
    ]
    count = sum(1 for p in reversals if re.search(p, text))
    return min(1.0, count * 0.25)


def _calculate_repetition(words):
    """Detects unusually high word repetition."""
    if not words:
        return 0.0
    counts = Counter(words)
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was',
        'and', 'or', 'but', 'in', 'on', 'at',
        'to', 'for', 'of', 'with', 'it', 'this'
    }
    content_counts = {w: c for w, c in counts.items()
                      if w not in stop_words and len(w) > 2}
    if not content_counts:
        return 0.0
    max_rep = max(content_counts.values())
    return min(1.0, (max_rep - 1) / 5.0)
