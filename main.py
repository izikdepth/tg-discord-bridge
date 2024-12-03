import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
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

telegram_bridge = TelegramBridge(bot)


@bot.event
async def on_ready():
    print("Bot is ready!")
    await bot.tree.sync()
    print('Slash commands synced')
    # start Telegram bot polling
    await telegram_bridge.telegram_updater_instance.start_polling() 


async def load_cogs():
    # Two-way bridge between Discord and Telegram.
    await discord_bridge.setup(bot, telegram_bridge)


async def main():
    await load_cogs()
    await telegram_bridge.application.initialize()

    discord_token = os.getenv("DDLN_BOT")
    if not discord_token:
        raise ValueError("DDLN_BOT token is missing from environment variables.")

    try:
        # start discord bot
        await bot.start(discord_token)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("Shutting down gracefully...")
    finally:
        # Clean up tasks
        await bot.close()
        await telegram_bridge.application.stop()
        print("Cleaned up resources.")


if __name__ == "__main__":
    asyncio.run(main())