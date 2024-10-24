from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from discord import Intents
from cogs.telegram import TelegramBridge
import cogs.discord as discord_bridge

load_dotenv()

intents = Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# announce_tg = Announcement(bot)
telegram_bridge = TelegramBridge(bot)

@bot.event
async def on_ready():
    print("Bot is ready!")
    await bot.tree.sync()
    print('Slash commands synced')

async def load_cogs():
    # # Two-way bridge between Discord and Telegram.
    await discord_bridge.setup(bot, telegram_bridge)
    

async def main():
    async with bot:
        await load_cogs()
        token = os.getenv("DDLN_BOT")
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())