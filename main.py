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
    result = any(word in FILTERED_WORDS for word in words)
    print(f"[FILTER CHECK] Text: {text!r}, Matched: {result}")
    return result

def ollama_generate_request(prompt, model=ollama_model):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt
    }
    print(f"[OLLAMA REQUEST] URL: {url}")
    print(f"[OLLAMA REQUEST] Payload: {json.dumps(payload)}")
    try:
        response = requests.post(url, json=payload, timeout=180)
        print(f"[OLLAMA RAW RESPONSE]\n{response.text}\n")
        response.raise_for_status()
        lines = response.text.strip().split('\n')
        last = lines[-1]
        data = json.loads(last)
        content = data.get("response", "").strip()
        print(f"[OLLAMA FINAL RESPONSE] {content!r}")
        return content
    except Exception as e:
        print(f"[OLLAMA ERROR] Exception during Ollama request: {e}")
        return ""

class MyClient(discord.Client):
    async def setup_hook(self):
        print("[DISCORD] Setup hook called, starting background queue task.")
        self.bg_task = asyncio.create_task(self.process_queue())

    async def on_ready(self):
        print(f"[DISCORD] Logged on as {self.user}!")

    async def on_message(self, message):
        print(f"[DISCORD] Message received: {message.content!r} from {message.author} in {message.channel}")
        if message.author == self.user:
            print("[DISCORD] Ignoring own message.")
            return
        if trigger_word and trigger_word.lower() in message.content.lower():
            print(f"[DISCORD] Trigger word '{trigger_word}' detected in message.")
            await message.channel.typing()
            ollama_response = await asyncio.to_thread(ollama_generate_request, message.content)
            if contains_filtered_word(ollama_response):
                print("[DISCORD] Response contained filtered word. Sending fallback message.")
                ollama_response = "meow"
            elif not ollama_response:
                print("[DISCORD] Empty response from Ollama. No reply will be sent.")
                return
            print(f"[DISCORD] Replying with: {ollama_response!r}")
            await message.reply(ollama_response)
        elif message.reference is not None:
            try:
                replied_message = await message.channel.fetch_message(message.reference.message_id)
                if replied_message.author == self.user:
                    print("[DISCORD] Replying to a previous bot message.")
                    await message.channel.typing()
                    ollama_response = await asyncio.to_thread(ollama_generate_request, message.content)
                    if contains_filtered_word(ollama_response):
                        print("[DISCORD] Response contained filtered word. Sending fallback message.")
                        ollama_response = "meow"
                    elif not ollama_response:
                        print("[DISCORD] Empty response from Ollama. No reply will be sent.")
                        return
                    print(f"[DISCORD] Replying with: {ollama_response!r}")
                    await message.reply(ollama_response)
            except Exception as e:
                print(f"[DISCORD] Exception while processing reply-to: {e}")

    async def process_queue(self):
        print("[DISCORD] Background queue task started.")
        while True:
            await asyncio.sleep(0.1)

client = MyClient(intents=intents)
print("[DISCORD] Starting client event loop.")
client.run(token)