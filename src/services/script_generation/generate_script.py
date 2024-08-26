from src.api.llm_api.openai_sync import fetch_openai_response_with_system_prompt, prepare_llm_prompt
from src.api.llm_api.prompts import Prompts

def generate_script(product_description: str, product_name: str, cta: str, target_audience: str, duration_limit: int):
    # Generate a script for the product
    user_prompt = prepare_llm_prompt(product_description)
    script = fetch_openai_response_with_system_prompt(user_prompt,system_prompt=Prompts.GENERATE_SCRIPT_PROMPT)
    return script