import os
from discord.ext import commands
from discord import Message
from utilities.utilities import convert_keys_to_strings

class DiscordBridge(commands.Cog):
    def __init__(self, bot, telegram_bridge):
        self.bot = bot
        self.telegram_bridge = telegram_bridge
        self.discord_channel_id = int(os.getenv("DISCORD_TGCHAT"))
        
        print("DiscordBridge Cog initialized")

    @commands.Cog.listener()
    async def on_ready(self):
        if not hasattr(self.bot, 'ready'):
            self.bot.ready = True
            print("Discord Bridge bot is ready")

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.channel.id != self.discord_channel_id or message.author.bot:
            return

        author = message.author.display_name
        text = message.clean_content

        # Ignore attachments
        if message.attachments:
            return

        # Convert keys in message_map to strings
        convert_keys_to_strings(self.telegram_bridge.message_map)

        # Handle replies
        reply_to_message_id = None
        if message.reference and message.reference.message_id:
            referenced_message_id = message.reference.message_id
        
            message_map = self.telegram_bridge.message_map
            reply_to_message_id = message_map['discord_to_tg'].get(str(referenced_message_id))
        
        if self.telegram_bridge:
            telegram_message_id = await self.telegram_bridge.send_message_to_telegram(author, text, reply_to_message_id)
            if telegram_message_id:
                # Update the message_map with the new mappings
                message_map['discord_to_tg'][str(message.id)] = telegram_message_id
                message_map['tg_to_discord'][str(telegram_message_id)] = message.id
        else:
            print("Telegram bridge is not initialized")


async def setup(bot, telegram_bridge):
    await bot.add_cog(DiscordBridge(bot, telegram_bridge))