import discord
import requests
import json
import asyncio
import os
import re
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
ollama_model = os.getenv("OLLAMA_MODEL")
trigger_word = os.getenv("TRIGGER_WORD")
intents = discord.Intents.default()
intents.message_content = True

FILTERED_WORDS_RAW = os.getenv("FILTERED_WORDS", "stupid, idiot, dumb poop fart")
FILTERED_WORDS = set(w.lower() for w in re.split(r"[,\s]+", FILTERED_WORDS_RAW.strip()) if w)

def contains_filtered_word(text):
    words = re.findall(r"\w+", text.lower())
    return any(word in FILTERED_WORDS for word in words)

def ollama_generate_request(prompt, model=ollama_model):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt
    }
    response = requests.post(url, json=payload, timeout=180)
    lines = response.text.strip().split('\n')
    last = lines[-1]
    data = json.loads(last)
    content = data.get("response", "").strip()
    return content

class MyClient(discord.Client):
    async def setup_hook(self):
        self.bg_task = asyncio.create_task(self.process_queue())

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        if trigger_word and trigger_word.lower() in message.content.lower():
            await message.channel.typing()
            ollama_response = await asyncio.to_thread(ollama_generate_request, message.content)
            if contains_filtered_word(ollama_response) or not ollama_response:
                return
            await message.reply(ollama_response)
        elif message.reference is not None:
            try:
                replied_message = await message.channel.fetch_message(message.reference.message_id)
                if replied_message.author == self.user:
                    await message.channel.typing()
                    ollama_response = await asyncio.to_thread(ollama_generate_request, message.content)
                    if contains_filtered_word(ollama_response) or not ollama_response:
                        return
                    await message.reply(ollama_response)
            except:
                pass

    async def process_queue(self):
        while True:
            await asyncio.sleep(0.1)

client = MyClient(intents=intents)
client.run(token)