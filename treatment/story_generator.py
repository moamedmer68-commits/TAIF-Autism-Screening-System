"""
Story Generator
Creates short child-friendly stories for therapy support.
"""


def generate_story(age, risk_level="Moderate Risk"):
    """
    Generate age-appropriate therapeutic story.

    Args:
        age (int): Child age
        risk_level (str): Risk level for thematic guidance

    Returns:
        dict: story title and text
    """
    if age <= 3:
        return {
            "title": "🌟 Zaid and His Colorful Blocks",
            "text": (
                "Zaid loves his colorful blocks. "
                "Every morning, he lines them up: red, blue, yellow, green. "
                "One day, his friend Sara came to play. "
                "Sara picked up the red block and smiled at Zaid. "
                "Zaid looked at Sara and slowly smiled back. "
                "Together, they built a tall, beautiful tower. "
                "When it fell down, they both laughed. "
                "Zaid learned that playing together is even more fun!"
            )
        }
    elif age <= 6:
        return {
            "title": "🦋 Layla and the Garden of Friends",
            "text": (
                "Layla was a little girl who loved butterflies. "
                "She spent every afternoon in the garden, watching them fly. "
                "One day, a boy named Omar sat beside her. "
                "'Do you like butterflies too?' he asked. "
                "Layla nodded slowly. 'The yellow ones are my favorite,' she said. "
                "'Mine too!' said Omar. "
                "From that day, Layla and Omar met in the garden every afternoon. "
                "They counted butterflies, named them, and drew pictures. "
                "Layla discovered that a good friend makes everything brighter."
            )
        }
    else:
        return {
            "title": "🚀 Ahmed and the Robot Friend",
            "text": (
                "Ahmed was ten years old and loved robots. "
                "At school, it was hard for him to join conversations. "
                "His teacher started a robot-building club. "
                "Ahmed built the fastest robot in the class. "
                "His classmates were amazed and asked him to teach them. "
                "Ahmed found that sharing what he loved "
                "helped him connect with others. "
                "He learned: your unique interest is your superpower."
            )
        }
