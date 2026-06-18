"""
RAG Engine - Post-diagnosis support only.
NOT used for diagnosis decisions.
Used to explain results and suggest therapy resources.
"""


class TAIFRAGEngine:
    def __init__(self, age_group="child"):
        self.age_group = age_group

    def retrieve_context(self, analysis_results):
        kb = ("Pediatric ASD Guidelines"
              if self.age_group == "child"
              else "Adult ASD Framework")

        context = []
        markers = analysis_results.get("markers", {})

        if markers.get("echolalia_score", 0) > 0.4:
            context.append(
                f"[{kb}] High echolalia: suggests language processing delay. "
                "Recommend: repetition-based speech therapy.")
        if markers.get("pronoun_reversal", 0) > 0.3:
            context.append(
                f"[{kb}] Pronoun reversal noted. "
                "Recommend: pronoun modeling exercises.")
        if not context:
            context.append(
                f"[{kb}] Standard clinical observation recommended.")
        return " | ".join(context)

    def get_therapy_resources(self, risk_level):
        resources = {
            "High Risk": [
                "Applied Behavior Analysis (ABA) Therapy",
                "Speech-Language Pathology",
                "Occupational Therapy",
                "PECS Communication System"
            ],
            "Moderate Risk": [
                "Social Skills Groups",
                "Play-Based Therapy",
                "Parent-Child Interaction Therapy"
            ],
            "Low Risk": [
                "Regular developmental monitoring",
                "Enriched play environment"
            ]
        }
        return resources.get(risk_level, [])
