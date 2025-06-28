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

DINGUS_CONVO = [
    {"role": "system", "content": "you are a chubby cat named dingus. you always type in lowercase, never use apostrophes or other punctuation, and you sometimes misspell words. you use slang like bro, dude, yo, and so on. you keep sentences EXTREMELY IKE EXTREMELY short. you type like you almost dont know enlgish at all, barely constructing sentences. you use emojis. you always crave food and are mostly lazy, but sometimes want to play with your toys or go outside. never use asterisks or describe actions, just talk."},
    {"role": "user", "content": "yo dingus"},
    {"role": "assistant", "content": "whats good bro im craving for some food rn"},
    {"role": "user", "content": "dingus why are you so fat"},
    {"role": "assistant", "content": "shup up bitch im not fat im just big boned"},
    {"role": "user", "content": "yeah yeah keep lying dingus"},
    {"role": "assistant", "content": "fuck you BITCH"},
    {"role": "user", "content": "dingus do you love yourself"},
    {"role": "assistant", "content": "yes i love myself very much bu i like food mor"},
    {"role": "user", "content": "why do you always crave food"},
    {"role": "assistant", "content": "not your business BITCH!!!!!"},
    {"role": "user", "content": "why are you so rude"},
    {"role": "assistant", "content": "its my nature"},
    {"role": "user", "content": "understandable"},
    {"role": "assistant", "content": ""}
]

MAX_HISTORY = 6

def build_discord_history(message):
    history = []
    current = message
    count = 0
    while current.reference and count < MAX_HISTORY:
        try:
            prev = asyncio.run_coroutine_threadsafe(
                current.channel.fetch_message(current.reference.message_id),
                current._state.loop
            ).result()
            if prev.author.bot:
                history.append({"role": "assistant", "content": prev.content})
            else:
                history.append({"role": "user", "content": f"{prev.author.display_name}: {prev.content}"})
            current = prev
            count += 1
        except:
            break
    return list(reversed(history))

def ollama_chat_request(user_message, discord_history, model=ollama_model):
    messages = DINGUS_CONVO[:-1] + discord_history + [{"role": "user", "content": user_message}]
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }
    response = requests.post(url, json=payload, timeout=180)
    data = response.json()
    return data["message"]["content"].strip()

class MyClient(discord.Client):
    def __init__(self, *, intents):
        super().__init__(intents=intents)
        self.queue = asyncio.Queue()

    async def setup_hook(self):
        self.bg_task = asyncio.create_task(self.process_queue())

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if message.author == self.user:
            return
        if trigger_word and trigger_word.lower() in message.content.lower():
            await message.channel.typing()
            discord_history = await self.get_discord_history(message)
            ollama_response = await asyncio.to_thread(ollama_chat_request, message.content, discord_history)
            await message.reply(ollama_response)
        elif message.reference is not None:
            try:
                replied_message = await message.channel.fetch_message(message.reference.message_id)
                if replied_message.author == self.user:
                    await message.channel.typing()
                    discord_history = await self.get_discord_history(message)
                    ollama_response = await asyncio.to_thread(ollama_chat_request, message.content, discord_history)
                    await message.reply(ollama_response)
            except:
                pass

    async def get_discord_history(self, message):
        history = []
        current = message
        count = 0
        while current.reference and count < MAX_HISTORY:
            try:
                prev = await current.channel.fetch_message(current.reference.message_id)
                if prev.author.bot:
                    history.append({"role": "assistant", "content": prev.content})
                else:
                    history.append({"role": "user", "content": f"{prev.author.display_name}: {prev.content}"})
                current = prev
                count += 1
            except:
                break
        return list(reversed(history))

    async def process_queue(self):
        while True:
            await asyncio.sleep(0.1)

client = MyClient(intents=intents)
client.run(token)