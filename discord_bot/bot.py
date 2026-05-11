import os

import discord
from dotenv import load_dotenv

from app.agents.chat import ChatAgent

load_dotenv(override=True)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

_sessions: dict[str, ChatAgent] = {}


def _get_agent(user_id: str) -> ChatAgent:
    if user_id not in _sessions:
        _sessions[user_id] = ChatAgent()
    return _sessions[user_id]


@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if client.user not in message.mentions:
        return

    user_input = message.content.replace(f"<@{client.user.id}>", "").strip()
    if not user_input:
        return

    async with message.channel.typing():
        agent = _get_agent(str(message.author.id))
        response = await agent.chat(user_input)

    await message.reply(response)


def main():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise ValueError("DISCORD_BOT_TOKEN no está configurado en el .env")
    client.run(token)


if __name__ == "__main__":
    main()
