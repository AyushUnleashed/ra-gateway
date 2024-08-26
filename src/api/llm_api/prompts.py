GENERATE_SCRIPT_PROMPT = "Based on the product description only return short paragraph for video script. no narration tags etc, only the text"

CHARACTER_SELECTION_PROMPT = "Please return a character which would relevant for this video ad. You can choose from Obama or Sam Altman. Only return the character name & nothing else"


class Prompts:
    def __init__(self):
        self.GENERATE_SCRIPT_PROMPT = GENERATE_SCRIPT_PROMPT
        self.CHARACTER_SELECTION_PROMPT = CHARACTER_SELECTION_PROMPT

