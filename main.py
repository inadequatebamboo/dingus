import discord
import requests
import json
import asyncio
import os
from dotenv import load_dotenv
from collections import defaultdict, deque
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
ollama_model = os.getenv("OLLAMA_MODEL")
trigger_word = os.getenv("TRIGGER_WORD")
intents = discord.Intents.default()
intents.message_content = True

user_memory = defaultdict(lambda: deque(maxlen=3))

def ollama_request(prompt, model=ollama_model):
    url = "http://localhost:11434/api/generate" # ollama api
    payload = {
        "model": model,
        "prompt": prompt
    }
    response = requests.post(url, json=payload, timeout=180)
    responses = []
    for line in response.text.strip().split('\n'): # fixed the bot not having a response
        if line.strip():
            data = json.loads(line)
            part = data.get("response", "")
            if part:
                responses.append(part)
    return "".join(responses).strip()

class MyClient(discord.Client):
    def __init__(self, *, intents):
        super().__init__(intents=intents)
        self.queue = asyncio.Queue()

    async def setup_hook(self):
        self.bg_task = asyncio.create_task(self.process_queue())  # fixed asyncio error

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if message.author == self.user:
            return
        user_memory[message.author.id].append(message.content)
        if trigger_word and trigger_word.lower() in message.content.lower():
            await message.channel.typing()
            recent = list(user_memory[message.author.id])[:-1]
            current_message = message.content
            if recent:
                prompt = (
                    "heres your recent conversation with the user:\n"
                    + "\n".join(recent)
                    + f"\n\nuser: {current_message}"
                )
            else:
                prompt = message.content
            ollama_response = await asyncio.to_thread(ollama_request, prompt)
            await message.reply(ollama_response)
        if message.reference is not None:
            try:
                replied_message = await message.channel.fetch_message(message.reference.message_id)
                if replied_message.author == self.user:
                    await message.channel.typing()
                    recent = list(user_memory[message.author.id])[:-1]
                    current_message = message.content
                    if recent:
                        prompt = (
                            "heres your recent conversation with the user:\n"
                            + "\n".join(recent)
                            + f"\n\nuser: {current_message}"
                        )
                    else:
                        prompt = message.content
                    ollama_response = await asyncio.to_thread(ollama_request, prompt)
                    await message.reply(ollama_response)
            except:
                pass

    async def process_queue(self):
        while True:
            await asyncio.sleep(0.1)

client = MyClient(intents=intents)
client.run(token)