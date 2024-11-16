GENERATE_SCRIPT_PROMPT = """
Based on the product description, create a short casual YouTube-style script with these specifications:
- Use natural pauses marked with "..."
- Use CAPS for emphasized words
- Mark rising inflections with question-like spelling (sooo, reallyyy)
- Mark extended sounds with letter repetition (amaazing, suuper)
- Keep sentences short and conversational
- No narration tags, tone indicators, or emojis
- Only return the raw script text

Example inflections:
- Normal: "really good" → Rising: "reallyyy good"
- Normal: "so easy" → Extended: "sooo easy"
- Normal: "amazing" → Extended: "amaazing"
"""

CHARACTER_SELECTION_PROMPT = "Please return a character which would relevant for this video ad. You can choose from Obama or Sam Altman. Only return the character name & nothing else"


class Prompts:
    GENERATE_SCRIPT_PROMPT = GENERATE_SCRIPT_PROMPT
    CHARACTER_SELECTION_PROMPT = CHARACTER_SELECTION_PROMPT

