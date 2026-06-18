"""
Therapy Engine
Generates therapy recommendations based on risk level.
"""


def therapy_plan(risk_level, age=None):
    """
    Generate therapy plan based on risk level.

    Args:
        risk_level (str): "Low Risk" / "Moderate Risk" / "High Risk"
        age (int): Child age for age-appropriate recommendations

    Returns:
        dict: Therapy plan details
    """
    plans = {
        "High Risk": {
            "title": "🔴 High Risk - Immediate Support Recommended",
            "summary": (
                "The screening suggests significant indicators. "
                "Immediate professional evaluation is strongly advised."
            ),
            "therapies": [
                "Applied Behavior Analysis (ABA)",
                "Speech & Language Therapy",
                "Occupational Therapy",
                "Social Skills Training",
                "Parent-Mediated Intervention"
            ],
            "parent_guidance": [
                "Schedule appointment with developmental pediatrician immediately",
                "Maintain consistent daily routines",
                "Use visual schedules and picture cards",
                "Engage in face-to-face interaction daily",
                "Join a parent support group"
            ]
        },
        "Moderate Risk": {
            "title": "🟠 Moderate Risk - Follow-Up Recommended",
            "summary": (
                "Some indicators are present. "
                "A follow-up evaluation is recommended."
            ),
            "therapies": [
                "Speech & Language Therapy",
                "Play-Based Therapy",
                "Social Skills Groups",
                "Parent-Child Interaction Therapy"
            ],
            "parent_guidance": [
                "Schedule follow-up with pediatrician",
                "Encourage social play with peers",
                "Read books together daily",
                "Reduce screen time, increase face-to-face",
                "Monitor developmental milestones"
            ]
        },
        "Low Risk": {
            "title": "🟢 Low Risk - Continue Monitoring",
            "summary": (
                "Screening shows minimal indicators. "
                "Continue regular developmental monitoring."
            ),
            "therapies": [
                "Regular developmental check-ups"
            ],
            "parent_guidance": [
                "Maintain regular pediatric check-ups",
                "Continue enriched play activities",
                "Monitor language development"
            ]
        }
    }
    return plans.get(risk_level, plans["Low Risk"])
