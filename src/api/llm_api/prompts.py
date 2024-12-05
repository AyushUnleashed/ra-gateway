EXAMPLE_SCRIPTS ="""
Script 1 (Crayo AI):
"Have you seen these VIRAL podcast clips... with gameplay playing at the bottom? Here's how you can make them in juuust three steps. This is Crayo AI and it lets you create these amaazing clips from your videos. To use it... go to [crayo.ai](http://crayo.ai/) and register. Click on split screen videos, paste your video link and click on next. The tool comes with sooo many gaming videos you can use... plus you can tweak the caption style however you want! It can generate up to 50 PLUS short videos in a day. This is a paid tool but... a lot of people are reallyyy making money with AdSense by creating videos of other creators and uploading them on YouTube. If you're looking to get into the viral shorts game... this tool might be exactlyyy what you need."

Script 2 (Micro1):
"This AI can automate the ENTIRE job of an HR... can you believe it? Built by a company named micro one, it can handle the whoole hiring process on its own. It can autonomously post job listings... conduct interviews... and EVEN test Engineers! To use it... simply provide the job details and the AI will create the job description and click post. Micro1 will autonomously collect all applicants and send the TOP 10% of them for an AI interview. The AI can ask questions and even test engineering skills... and it comes in muultiple languages! This can truuly help hiring managers get AMAZING talent without going through thousands of applicants. Check out Micro1 if you're sooo tired of spending weeeeks on hiring."

Script 3 (Ideogram):
"You can nowww get PERFECT text in your AI generated images... isn't that amazing? Ideogram has come up with its new image generation model... Ideogram 2.0... and as you can see it's INCREDIBLE at embedding text into images! And the outputs... in terms of realism, skin tone, and textures... look even BETTER than midJourney! You can try it for free by visiting [ideogram.ai](http://ideogram.ai/)... If you've been struggling with text in your AI art... this is seriouslyyy the tool you've been waiting for!"

Script 4 (Tripo AI):
"You can now convert ANY AI generated images into 3D characters for free... isn't that crazy? Here's the text hack on how to do that... First to get AI images we will use crei which has this amaazing free flux model for image generation. Here with a simple prompt... you can generate images like THIS. Next go to Tripo AI and upload your image... click on Create and... DONE - your image is now a 3D model! Tripo AI even has sooo many 3D characters which you can play along with. If you've been wanting to bring your AI art to life in 3D... nowww's your chance to try it out!"

Script 5 (Playground AI):
"You HAVE to try this image generation model... it's literally democratizing graphic design! It's not just another midJourney or di... it's Playground AI which has released its version 3 specifically built for graphic design. Imagine Canva but with INSTANT AI capabilities... how cool is that? You can interact with it like a huuman designer... For example say 'change this for Mom.' With thousandss of templates you can design ANYTHING from t-shirts to logos to memes... Simply select a template... type in the changes you want and you are done! This could be the new go-to tool for creators marketers or anyone needing quick professional Graphics... If you're looking for a design tool that feels like having a designer in your pocket... you reallyyy need to check this one out!"
"""

GENERATE_SCRIPT_PROMPT = f"""
Based on the product description, create a casual Tiktok-style script with these specifications:
- Use natural pauses marked with "..."
- Use CAPS for emphasized words
- Mark rising inflections with question-like spelling (sooo, reallyyy)
- Mark extended sounds with letter repetition (amaazing, suuper)
- Keep sentences short and conversational
- No narration tags, tone indicators, No emojis, No hashtags
- Only return the raw script text

Example inflections:
- Normal: "really good" → Rising: "reallyyy good"
- Normal: "so easy" → Extended: "sooo easy"
- Normal: "amazing" → Extended: "amaazing"

Example scripts:

{EXAMPLE_SCRIPTS}
"""

CHARACTER_SELECTION_PROMPT = "Please return a character which would relevant for this video ad. You can choose from Obama or Sam Altman. Only return the character name & nothing else"


class Prompts:
    GENERATE_SCRIPT_PROMPT = GENERATE_SCRIPT_PROMPT
    CHARACTER_SELECTION_PROMPT = CHARACTER_SELECTION_PROMPT

