import discord
import requests
import json
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
ollama_model = os.getenv("OLLAMA_MODEL")
trigger_word = os.getenv("TRIGGER_WORD")
intents = discord.Intents.default()
intents.message_content = True

def ollama_request(prompt, model=ollama_model):
    url = "http://localhost:11434/api/generate" # ollama api url
    payload = {
        "model": model,
        "prompt": prompt
    }
    response = requests.post(url, json=payload, timeout=180)
    response.raise_for_status()
    lines = response.text.strip().split('\n')
    last = lines[-1]
    data = json.loads(last)
    return data.get("response", "").strip()
class MyClient(discord.Client):
    def __init__(self, *, intents): #queue task
        super().__init__(intents=intents)
        self.queue = asyncio.Queue()
        self.bg_task = self.loop.create_task(self.process_queue())

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if message.author == client.user:
            return
        if trigger_word.lower() in message.content.lower():    # trigger message detection
            await message.channel.typing()
            ollama_response = ollama_request(message.conent)
            await message.reply(ollama_response)
        if message.reference is not None:                      # reply detection
            try:
                replied_message = await message.channel.fetch_message(message.reference.message_id)
                if replied_message.author == client.user:
                    await message.channel.typing()
                    ollama_response = ollama_request(message.conent)
                    await message.reply(ollama_response)
            except:
                pass

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(token)
