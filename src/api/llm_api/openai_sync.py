import os
from dotenv import find_dotenv, load_dotenv
from src.api.llm_api.prompts import GENERATE_SCRIPT_PROMPT
import requests
import json

MODEL_GPT_35_TURBO = "gpt-3.5-turbo"
MODEL_NAME=  MODEL_GPT_35_TURBO

def prepare_llm_prompt(product_description: str, product_name: str, cta: str, target_audience: str, duration_limit: int, direction: str) -> str:
    # Prepare the prompt for LLM.
    llm_prompt = f"\n Input Description:"
    llm_prompt += f"\n {product_description}"
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


def fetch_openai_response(user_prompt: str):
    try:
        reset_chat_history()
        global chat_history
        chat_history.append({"role": "user", "content": user_prompt})
        print("Waiting for OpenAI response...")

        # Assuming you're using GPT-3.5 Turbo; adjust as needed
        MODEL_NAME = MODEL_GPT_35_TURBO

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        data = json.dumps({
            "model": MODEL_NAME,
            "messages": chat_history,
            "max_tokens": 350,
            "temperature":0.5,
        })

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=data)

        if response.status_code == 200:
            openai_response = response.json()
            print(openai_response)
            reply = openai_response['choices'][0]['message']['content']
            completion_tokens = openai_response['usage']['completion_tokens']
            prompt_tokens = openai_response['usage']['prompt_tokens']
            total_tokens = openai_response['usage']['total_tokens']

            print("OpenAI Paid API reply:", reply)
            print("Completion tokens:", completion_tokens)
            print("Prompt tokens:", prompt_tokens)
            print("Total tokens used:", total_tokens)

            chat_history.append({"role": "assistant", "content": reply})
            print("Response received.")
            return reply
        else:
            print("Error fetching response:", response.text)
            return None

    except Exception as e:
        print("Exception occurred while fetching response from OpenAI:", e)
        return None




def fetch_openai_response_with_system_prompt(user_prompt: str,system_prompt:str):
    try:
        reset_chat_history()
        global chat_history
        chat_history = [{"role": "system", "content": system_prompt}]
        chat_history.append({"role": "user", "content": user_prompt})
        print("Waiting for OpenAI response...")

        # Assuming you're using GPT-3.5 Turbo; adjust as needed
        MODEL_NAME = MODEL_GPT_35_TURBO

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        data = json.dumps({
            "model": MODEL_NAME,
            "messages": chat_history,
            "max_tokens": 350,
            "temperature":0.5,
        })

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=data)

        if response.status_code == 200:
            openai_response = response.json()
            print(openai_response)
            reply = openai_response['choices'][0]['message']['content']
            completion_tokens = openai_response['usage']['completion_tokens']
            prompt_tokens = openai_response['usage']['prompt_tokens']
            total_tokens = openai_response['usage']['total_tokens']

            print("OpenAI Paid API reply:", reply)
            print("Completion tokens:", completion_tokens)
            print("Prompt tokens:", prompt_tokens)
            print("Total tokens used:", total_tokens)

            chat_history.append({"role": "assistant", "content": reply})
            print("Response received.")
            return reply
        else:
            print("Error fetching response:", response.text)
            return None

    except Exception as e:
        print("Exception occurred while fetching response from OpenAI:", e)
        return None



if __name__ == "__main__":

    prompt = " Superheroai: It helps you generate superhero avatar of yourself using AI"
    llm_prompt = prepare_llm_prompt(prompt)
    print(fetch_openai_response(llm_prompt))