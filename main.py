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

def redact_filtered_words(text):
    def replacer(match):
        word = match.group(0)
        if word.lower() in FILTERED_WORDS:
            print(f"[REDACT] Redacting word: {word!r}")
            return "[[REDACTED]]"
        else:
            return word
    pattern = r'\b(' + '|'.join(re.escape(word) for word in FILTERED_WORDS) + r')\b'
    redacted = re.sub(pattern, replacer, text, flags=re.IGNORECASE)
    if redacted != text:
        print(f"[REDACT] Original: {text!r}")
        print(f"[REDACT] Redacted: {redacted!r}")
    return redacted

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
        content = ''.join(json.loads(line).get("response", "") for line in lines if line.strip())
        print(f"[OLLAMA FINAL RESPONSE] {content!r}")
        return content.strip()
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
            if not ollama_response:
                print("[DISCORD] Empty response from Ollama. No reply will be sent.")
                return
            redacted_response = redact_filtered_words(ollama_response)
            print(f"[DISCORD] Replying with: {redacted_response!r}")
            await message.reply(redacted_response)
        elif message.reference is not None:
            try:
                replied_message = await message.channel.fetch_message(message.reference.message_id)
                if replied_message.author == self.user:
                    print("[DISCORD] Replying to a previous bot message.")
                    await message.channel.typing()
                    ollama_response = await asyncio.to_thread(ollama_generate_request, message.content)
                    if not ollama_response:
                        print("[DISCORD] Empty response from Ollama. No reply will be sent.")
                        return
                    redacted_response = redact_filtered_words(ollama_response)
                    print(f"[DISCORD] Replying with: {redacted_response!r}")
                    await message.reply(redacted_response)
            except Exception as e:
                print(f"[DISCORD] Exception while processing reply-to: {e}")

    async def process_queue(self):
        print("[DISCORD] Background queue task started.")
        while True:
            await asyncio.sleep(0.1)

client = MyClient(intents=intents)
print("[DISCORD] Starting client event loop.")
client.run(token)