# Dingus

## About
Dingus is a highly customisable chatbot in Discord that uses LLM models and Ollama to generate responses to users.
## Requirements
### 1. Ollama
For the AI features, install ollama

`curl -fsSL https://ollama.com/install.sh | sh`
### 2. Python dependencies
To install all requirements, do `pip install -r requirements.txt`

### 3. Discord bot
Please set up your Discord bot on the developer portal [here](https://discord.com/developers/applications)

## Installation
### 1. Clone the repository
`git clone https://github.com/inadequatebamboo/dingus.git`
### 2. Create a .env file in the repo folder
#### Example .env file:
```
DISCORD_TOKEN=your-token-here
OLLAMA_MODEL=your-model-here
TRIGGER_WORD=your-trigger-word-here
```
### 3. Run the py file
`python main.py`
## Usage
To use dingus, just use your trigger word in your sentence. For example:
`hello dingus`

You can also reply to the bots replies!
## TODO list
- Add short term memory
- Add random responses with a customisable chance
- Improve code
