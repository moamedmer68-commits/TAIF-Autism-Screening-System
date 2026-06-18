"""
Recommendation Engine
Generates clinical indicators and parent-facing recommendations.
"""


class TAIFRecommendationEngine:

    def generate_final_output(self, final_score, risk_level,
                               questionnaire_score,
                               vision_score=None,
                               audio_result=None,
                               age=None):
        """
        Generate full recommendation output.

        Returns:
            dict: Clinical status, indicators, recommendations
        """
        indicators = self._get_indicators(
            questionnaire_score, vision_score, audio_result)

        recommendations = self._get_recommendations(risk_level, age)

        return {
            "clinical_status": risk_level,
            "final_score": round(final_score, 3),
            "questionnaire_score": round(questionnaire_score, 3),
            "vision_score": (round(vision_score, 3)
                             if vision_score is not None else None),
            "audio_score": (round(audio_result.get(
                "audio_text_score", 0), 3)
                if audio_result else None),
            "indicators": indicators,
            "recommendations": recommendations
        }

    def _get_indicators(self, q_score, v_score, audio_result):
        indicators = []

        if q_score > 0.6:
            indicators.append(
                "⚠️ High questionnaire score - behavioral concerns noted")
        if v_score and v_score > 0.6:
            indicators.append(
                "⚠️ Image analysis suggests atypical facial patterns")
        if audio_result:
            if audio_result.get("echolalia_score", 0) > 0.3:
                indicators.append(
                    "⚠️ Echolalia detected in speech transcript")
            if audio_result.get("pronoun_reversal", 0) > 0.3:
                indicators.append(
                    "⚠️ Pronoun reversal patterns observed")
            if audio_result.get("vocabulary_ratio", 1) < 0.4:
                indicators.append(
                    "⚠️ Limited vocabulary diversity detected")
        if not indicators:
            indicators.append(
                "✅ No significant risk indicators detected")
        return indicators

    def _get_recommendations(self, risk_level, age):
        base = [
            "This is a screening tool, not a final diagnosis.",
            "Please consult a licensed pediatric specialist."
        ]
        if risk_level == "High Risk":
            base += [
                "Seek immediate professional evaluation.",
                "Early intervention is highly recommended.",
                "Consider speech therapy and behavioral support."
            ]
        elif risk_level == "Moderate Risk":
            base += [
                "Schedule a follow-up with a developmental pediatrician.",
                "Monitor social and communication development.",
                "Consider early support programs."
            ]
        return base
