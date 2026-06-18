"""
Medical Notes Processor
Cleans text and extracts clinical milestones.
"""

import re
import unicodedata


class MedicalNotesProcessor:
    def __init__(self, lang="en"):
        self.lang = lang
        self.pii_patterns = [
            r'\b\d{10,14}\b',
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
            r'\s+\d{1,2},?\s+\d{4}\b'
        ]

    def clean_text(self, text):
        if not text:
            return ""
        text = unicodedata.normalize('NFKC', text)
        for pattern in self.pii_patterns:
            text = re.sub(pattern, "[REDACTED]", text)
        text = " ".join(text.split())
        return text

    def extract_clinical_milestones(self, text, age_group="child"):
        findings = {}
        if age_group == "child":
            findings['delayed_speech'] = bool(re.search(
                r"(delay|late|تاخر)\s+(speech|talking|الكلام)",
                text, re.I))
            findings['eye_contact'] = bool(re.search(
                r"(eye contact|avoidant|بصري)", text, re.I))
        return findings

    def prepare_for_rag(self, text, chunk_size=500):
        cleaned = self.clean_text(text)
        return [cleaned[i:i+chunk_size]
                for i in range(0, len(cleaned), chunk_size)]
