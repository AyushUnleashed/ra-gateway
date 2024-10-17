import aiohttp
import asyncio
import logging
import os
from dotenv import load_dotenv
load_dotenv()

SLACKBOT_RA_WEBHOOK_URL = str(os.getenv("SLACKBOT_RA_WEBHOOK_URL"))


class SlackBot:
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    async def send_message(self, message: str):
        try:
            payload = {"text": message}
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        logging.info("Successfully sent data to Slack")
                    else:
                        logging.error(f"Error: Send to Slack failed with status code: {response.status}")
        except Exception as error:
            logging.error(f"An error occurred while sending message to Slack: {error}")

RA_SLACK_BOT = SlackBot(SLACKBOT_RA_WEBHOOK_URL)

if __name__ == "__main__":
    asyncio.run(RA_SLACK_BOT.send_message('Hello, from RA_SLACK_BOT!'))