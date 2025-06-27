import discord
import requests
import json
import asyncio

intents = discord.Intents.default()
intents.message_content = True

def ollama_request(prompt, model="dingus"):
    url = "http://localhost:11434/api/generate"
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
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if message.author == client.user:
            return
        if 'dingus' in message.content.lower():
            await message.channel.typing()
            ollama_response = ollama_request(message.conent)
            await message.reply(ollama_response)
        if message.reference is not None:
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
client = discord.Client(activity=discord.Game(name='my game'))
client.run(token)
