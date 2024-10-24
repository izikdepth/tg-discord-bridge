from discord.ext import commands
from dotenv import load_dotenv
from discord import Message
import os

def check_env_vars():
    required_vars = [
        "DISCORD_TGCHAT"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
    else:
        print("All required environment variables are set.")
        
load_dotenv()
check_env_vars()

class DiscordBridge(commands.Cog):
    def __init__(self, bot, telegram_bridge):
        self.bot = bot
        self.telegram_bridge = telegram_bridge
        self.discord_channel_id = int(os.getenv("DISCORD_TGCHAT"))

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.channel.id != self.discord_channel_id or message.author.bot:
            return

        author = message.author.display_name
        text = message.clean_content
        # print(f"Received Discord message from {author}: {text}")

        # Skip handling attachments
        if message.attachments:
            # print("Skipping attachment handling")
            return

        # Handle replies
        reply_to_message_id = None
        if message.reference:
            referenced_message_id = message.reference.message_id
            for tg_message_id, discord_message_id in self.telegram_bridge.message_map.items():
                if discord_message_id == str(referenced_message_id):
                    reply_to_message_id = tg_message_id
                    break

        if self.telegram_bridge:
            self.telegram_bridge.send_message_to_telegram(author, text, reply_to_message_id)
            # print("Sent message to Telegram chat")
        else:
            print("Telegram bridge is not initialized")

    @commands.Cog.listener()
    async def on_ready(self):
        if not hasattr(self.bot, 'ready'):
            self.bot.ready = True
            print("Discord Bridge bot is ready")

async def setup(bot, telegram_bridge):
    await bot.add_cog(DiscordBridge(bot, telegram_bridge))