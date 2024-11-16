import os
from dotenv import find_dotenv, load_dotenv
from fastapi import HTTPException
from src.api.llm_api.prompts import GENERATE_SCRIPT_PROMPT
import aiohttp
import asyncio
import json
from src.utils.logger import logger

MODEL_GPT_35_TURBO = "gpt-3.5-turbo"
MODEL_NAME = MODEL_GPT_35_TURBO

def prepare_llm_prompt(product_description: str, product_name: str, cta: str, target_audience: str, duration_limit: int, direction: str) -> str:
    # Prepare the prompt for LLM.
    llm_prompt = f"\n Input Description:"
    llm_prompt += f"\n {product_description}"
    llm_prompt += f"\n -------------------"
    llm_prompt += f"\n Product Name: {product_name}"
    llm_prompt += f"\n Call to Action: {cta}"
    llm_prompt += f"\n Target Audience: {target_audience}"
    llm_prompt += f"\n Duration Limit: {duration_limit}"
    llm_prompt += f"\n Direction: {direction}"
    llm_prompt += f"\n\n Output Script:"
    return llm_prompt

# Load environment variables from the root .env file
root_env_path = find_dotenv()
load_dotenv(root_env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = GENERATE_SCRIPT_PROMPT
chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]

def reset_chat_history():
    global chat_history
    chat_history.clear()
    chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]

def set_system_prompt(NEW_PROMPT):
    global chat_history
    chat_history = [{"role": "system", "content": NEW_PROMPT}]

async def fetch_openai_response(user_prompt: str):
    return await _fetch_openai_response_internal(user_prompt, SYSTEM_PROMPT, max_tokens=1000)

async def fetch_openai_response_with_system_prompt(user_prompt: str, system_prompt: str):
    return await _fetch_openai_response_internal(user_prompt, system_prompt, max_tokens=1000)

async def _fetch_openai_response_internal(user_prompt: str, system_prompt: str, max_tokens: int):
    try:
        reset_chat_history()
        global chat_history
        chat_history = [{"role": "system", "content": system_prompt}]
        chat_history.append({"role": "user", "content": user_prompt})
        logger.info("chat history: %s", chat_history)
        logger.info("Waiting for OpenAI response...")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        data = json.dumps({
            "model": MODEL_NAME,
            "messages": chat_history,
            "max_tokens": max_tokens,
            "temperature": 0.5,
        })

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, data=data) as response:
                response_text = await response.text()
                if response.status == 200:
                    openai_response = json.loads(response_text)
                    logger.info(openai_response)
                    reply = openai_response['choices'][0]['message']['content']
                    completion_tokens = openai_response['usage']['completion_tokens']
                    prompt_tokens = openai_response['usage']['prompt_tokens']
                    total_tokens = openai_response['usage']['total_tokens']

                    logger.info("OpenAI Paid API reply: %s", reply)
                    # logger.info("Completion tokens: %d", completion_tokens)
                    # logger.info("Prompt tokens: %d", prompt_tokens)
                    # logger.info("Total tokens used: %d", total_tokens)

                    chat_history.append({"role": "assistant", "content": reply})
                    logger.info("Response received.")
                    return reply
                else:
                    error_body = json.loads(response_text)
                    if "insufficient_quota" in str(error_body):
                        logger.error("OpenAI API quota exceeded")
                        raise HTTPException(
                            status_code=503,
                            detail={
                                "error": "service_unavailable",
                                "message": "Service temporarily unavailable",
                                "retry_after": "3600"  # Suggest retry after 1 hour
                            }
                        )
                    logger.error("Error from OpenAI: %s", response_text)
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Error from OpenAI: {error_body.get('error', {}).get('message', 'Unknown error')}"
                    )

    except HTTPException as http_ex:
        # Re-raise HTTP exceptions
        raise
    except json.JSONDecodeError:
        logger.exception("Failed to parse OpenAI response")
        raise HTTPException(status_code=500, detail="Failed to parse OpenAI response")
    except aiohttp.ClientError as e:
        logger.exception("Network error while calling OpenAI")
        raise HTTPException(status_code=500, detail="Failed to connect to OpenAI")
    except Exception as e:
        logger.exception("Unexpected error: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    prompt = " Superheroai: It helps you generate superhero avatar of yourself using AI"
    llm_prompt = prepare_llm_prompt(
        product_description="Superheroai: It helps you generate superhero avatar of yourself using AI",
        product_name="Superheroai",
        cta="Generate your superhero avatar now!",
        target_audience="AI enthusiasts",
        duration_limit=60,
        direction="Create an engaging and fun script"
    )
    asyncio.run(fetch_openai_response(llm_prompt))