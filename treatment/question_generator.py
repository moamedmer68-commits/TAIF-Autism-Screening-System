"""
Question Generator
Generates comprehension questions about the therapy story.
"""


def generate_questions(age, story_title=""):
    """
    Generate 3-5 comprehension questions about the story.

    Args:
        age (int): Child age
        story_title (str): Story title for context

    Returns:
        list: Questions
    """
    if age <= 3:
        return [
            "What colors were Zaid's blocks?",
            "Who came to play with Zaid?",
            "What did they build together?",
            "What happened when the tower fell?",
            "How did Zaid feel at the end?"
        ]
    elif age <= 6:
        return [
            "What did Layla love to watch in the garden?",
            "What was Omar's favorite butterfly color?",
            "What did Layla and Omar do together?",
            "How did Layla feel after making a friend?",
            "What is your favorite thing to do outside?"
        ]
    else:
        return [
            "What was Ahmed's special interest?",
            "Why was it hard for Ahmed at school?",
            "What changed when the robot club started?",
            "What did Ahmed teach his classmates?",
            "What is your own special interest or superpower?"
        ]
