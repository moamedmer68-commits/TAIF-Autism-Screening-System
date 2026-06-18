"""
Fusion Model - transparent rule-based weighted fusion.
No trained fusion model is used.

Correction:
The previous arbitrary +0.05 bonus for questionnaire_score > 0.7 was removed.
The output is now only the documented weighted average of available modules.
"""


def fuse(questionnaire_score, vision_score=None, audio_text_score=None):
    has_vision = vision_score is not None
    has_audio = audio_text_score is not None

    if has_vision and has_audio:
        final = 0.4 * questionnaire_score + 0.4 * vision_score + 0.2 * audio_text_score
    elif has_vision:
        final = 0.5 * questionnaire_score + 0.5 * vision_score
    elif has_audio:
        final = 0.6 * questionnaire_score + 0.4 * audio_text_score
    else:
        final = questionnaire_score

    return float(max(0.0, min(1.0, final)))


def get_risk_level(score):
    if score < 0.4:
        return "Low Risk", "🟢"
    if score < 0.7:
        return "Moderate Risk", "🟠"
    return "High Risk", "🔴"
