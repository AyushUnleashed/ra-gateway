from src.api.llm_api.openai_async import fetch_openai_response_with_system_prompt, prepare_llm_prompt
from src.api.llm_api.prompts import Prompts
from src.models.base_models import ProductBase, VideoConfiguration, Script
from src.utils.logger import logger

async def generate_script_with_llm(product_base: ProductBase, video_configuration: VideoConfiguration):
    # Generate a script for the product
    logger.info("Starting script generation for product: %s", product_base.name)
    script = await generate_script(
        product_description=product_base.description,
        product_name=product_base.name,
        cta=video_configuration.cta,
        target_audience=video_configuration.target_audience,
        duration_limit=video_configuration.duration,
        direction=video_configuration.direction
    )

    import uuid
    script_id = uuid.uuid4()
    script_object = Script(id=script_id, title=f"script for {product_base.name}", content=script)
    logger.info("Script generated with ID: %s for product: %s", script_id, product_base.name)
    return script_object

async def generate_script(product_description: str, product_name: str, cta: str, target_audience: str, duration_limit: int, direction: str):
    # Generate a script for the product
    logger.debug("Preparing LLM prompt for product: %s", product_name)
    cache = False
    if cache == True:
        logger.debug("Returning cached script for product: %s", product_name)
        return "A.I."
    user_prompt = prepare_llm_prompt(product_description, product_name, cta, target_audience, duration_limit, direction)
    logger.info("Fetching script from OpenAI for product: %s", product_name)
    script = await fetch_openai_response_with_system_prompt(user_prompt, system_prompt=Prompts.GENERATE_SCRIPT_PROMPT)
    logger.info("Script fetched successfully for product: %s", product_name)
    return script