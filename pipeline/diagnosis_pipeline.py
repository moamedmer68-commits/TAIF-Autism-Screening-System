"""Main diagnosis pipeline connecting questionnaire, vision, audio/text and fusion."""

from __future__ import annotations

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.questionnaire_pipeline import fallback_questionnaire_score, predict_questionnaire
from pipeline.vision_pipeline import predict_image_with_details, check_model_exists
from pipeline.audio_pipeline import analyze_audio
from pipeline.fusion_model import fuse, get_risk_level
from modules.recommendation_engine import TAIFRecommendationEngine


def diagnose(
    age,
    answers,
    gender=0,
    jaundice=0,
    family_history=0,
    language_delay=0,
    social_interaction=0,
    communication=0,
    repetitive=0,
    image_file=None,
    audio_file=None,
    manual_transcript=None,
    api_key=None,
    ethnicity="Others",
    completed_by="Family member",
):
    result = {
        "age": age,
        "questionnaire_score": 0.0,
        "vision_score": None,
        "vision_details": None,
        "audio_result": None,
        "final_score": 0.0,
        "risk_level": "Low Risk",
        "risk_emoji": "🟢",
        "recommendations": {},
        "errors": [],
        "scoring_source": "model",
    }

    try:
        result["questionnaire_score"] = predict_questionnaire(
            age=age,
            answers=answers,
            gender=gender,
            jaundice=jaundice,
            family_history=family_history,
            language_delay=language_delay,
            social_interaction=social_interaction,
            communication=communication,
            repetitive=repetitive,
            ethnicity=ethnicity,
            completed_by=completed_by,
        )
    except Exception as exc:
        # Do not return the default 0% result on a questionnaire failure. Use a
        # transparent backup score, keep the warning for the report, and continue.
        result["errors"].append(f"Questionnaire model error; fallback scoring used: {exc}")
        result["questionnaire_score"] = fallback_questionnaire_score(
            age=age,
            answers=answers,
            gender=gender,
            jaundice=jaundice,
            family_history=family_history,
            language_delay=language_delay,
            social_interaction=social_interaction,
            communication=communication,
            repetitive=repetitive,
            ethnicity=ethnicity,
            completed_by=completed_by,
        )
        result["scoring_source"] = "fallback"

    if age > 3 and image_file is not None:
        try:
            if check_model_exists():
                details = predict_image_with_details(image_file)
                result["vision_details"] = details
                result["vision_score"] = details["autism_probability"]
            else:
                result["errors"].append("Vision model not found - skipped")
        except Exception as exc:
            result["errors"].append(f"Vision error: {exc}")

    if age > 3 and (audio_file is not None or manual_transcript):
        try:
            result["audio_result"] = analyze_audio(
                audio_file=audio_file,
                manual_transcript=manual_transcript,
                api_key=api_key,
            )
        except Exception as exc:
            result["errors"].append(f"Audio error: {exc}")

    audio_score = None
    if result["audio_result"]:
        audio_score = result["audio_result"].get("audio_text_score")

    result["final_score"] = fuse(
        questionnaire_score=result["questionnaire_score"],
        vision_score=result["vision_score"],
        audio_text_score=audio_score,
    )

    risk, emoji = get_risk_level(result["final_score"])
    result["risk_level"] = risk
    result["risk_emoji"] = emoji

    engine = TAIFRecommendationEngine()
    result["recommendations"] = engine.generate_final_output(
        final_score=result["final_score"],
        risk_level=risk,
        questionnaire_score=result["questionnaire_score"],
        vision_score=result["vision_score"],
        audio_result=result["audio_result"],
        age=age,
    )
    return result
