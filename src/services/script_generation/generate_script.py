from src.api.llm_api.openai_async import fetch_openai_response_with_system_prompt, prepare_llm_prompt
from src.api.llm_api.prompts import Prompts
from src.models.base_models import ProductBase, VideoConfiguration, Script

async def generate_script_with_llm(product_base: ProductBase, video_configuration: VideoConfiguration):
    # Generate a script for the product
    script= await generate_script(
        product_description=product_base.description,
        product_name=product_base.name,
        cta=video_configuration.cta,
        target_audience=video_configuration.target_audience,
        duration_limit=video_configuration.duration,
        direction = video_configuration.direction
    )

    import uuid
    script_id = uuid.uuid4()
    script_object = Script(id=script_id, title=f"script for {product_base.name}", content=script)
    return script_object



async def generate_script(product_description: str, product_name: str, cta: str, target_audience: str, duration_limit: int, direction: str):
    # Generate a script for the product
    cache = False
    if cache==True:
        return "A.I."
    user_prompt = prepare_llm_prompt(product_description, product_name, cta, target_audience, duration_limit, direction)
    script = await fetch_openai_response_with_system_prompt(user_prompt,system_prompt=Prompts.GENERATE_SCRIPT_PROMPT)
    return script