import os
import asyncio
from discord import Embed
from telegram.ext import MessageHandler, ContextTypes
import html
from telegram.ext.filters import Chat, TEXT
from telegram.constants import ParseMode
from dotenv import load_dotenv
from updater.updater import TelegramUpdater
from telegram.error import NetworkError, RetryAfter
# from cogs.bridge.token_filter import TokenFilter

def check_env_vars():
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT",
        "DISCORD_TGCHAT",
        "DDLN_BOT"
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
    else:
        print("All required environment variables are set.")

load_dotenv()
check_env_vars()


telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")


# Add the TokenFilter to the root logger to redact the Telegram token
# logger.addFilter(TokenFilter(telegram_token))

class TelegramBridge:
    def __init__(self, discord_bot, bot_ready_event=None):
        self.bot = discord_bot
        self.telegram_token = telegram_token
        self.tg_chat_id = int(os.getenv("TELEGRAM_CHAT"))
        self.discord_channel_id = int(os.getenv("DISCORD_TGCHAT"))
        self.discord_bot_token = os.getenv("DDLN_BOT")
        self.bot_ready_event = bot_ready_event

        # Create an instance of TelegramUpdater
        self.telegram_updater_instance = TelegramUpdater()
        self.application = self.telegram_updater_instance.get_application()

        self.message_map = {
            'tg_to_discord' : {},
            'discord_to_tg' :{}
        }

        print("Telegram Bridge initialized with:")
        print(f"Telegram Chat ID: {self.tg_chat_id}")

        # Start Telegram listener
        self.start_telegram_listener()

    def start_telegram_listener(self):
        self.application.add_handler(MessageHandler(
            Chat(chat_id=self.tg_chat_id) & TEXT,
            self.handle_telegram_message
        ))
        
        self.application.add_error_handler(self.error_handler)
        print("Telegram listener registered")

    async def error_handler(self, update, context: ContextTypes.DEFAULT_TYPE):
        # Log the error
        print(f"Update {update} caused an error: {context.error}")
        # Determine the type of error and handle accordingly
        try:
            raise context.error
        except RetryAfter as e:
            retry_after = e.retry_after
            await asyncio.sleep(retry_after)
        except NetworkError:
            # Handle network errors
            await asyncio.sleep(5)
        except Exception as e:
            print("An unexpected error occurred: %s", e)

    async def handle_telegram_message(self, update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if update.message is None:
                return

            tg_message = update.message
            author = tg_message.from_user.full_name or "Unknown User"
            text = tg_message.text or "[No Text]"

            # Skip non-text messages
            if tg_message.photo or tg_message.video or tg_message.document:
                return
            
            # Send to Discord
            discord_message_id = await self.send_message_to_discord(author, text)
            
            # Map Telegram message ID to Discord message ID
            if discord_message_id:
                self.message_map['tg_to_discord'][tg_message.message_id] = discord_message_id
                self.message_map['discord_to_tg'][discord_message_id] = tg_message.message_id
                
        except Exception as e:
            print(f"Error in handle_telegram_message: {e}")
            
    async def send_message_to_discord(self, author, text):
        channel = self.bot.get_channel(self.discord_channel_id)
        if not channel:
            return None

        embed = Embed(description=text, color=0x3498db)
        embed.set_author(name=author, icon_url="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg")
        try:
            message = await channel.send(embed=embed)
            return message.id
        except Exception:
            return None


    async def send_message_to_telegram(self, author, text, original_message_id=None):
        escaped_author = html.escape(author, quote=True)
        escaped_text = html.escape(text, quote=True)
        formatted_text = f"<b>{escaped_author}</b>\n{escaped_text}"

        # Send the message to Telegram using the application instance
        try:
            message = await self.application.bot.send_message(
                chat_id=self.tg_chat_id,
                text=formatted_text,
                parse_mode=ParseMode.HTML,
                reply_to_message_id=original_message_id
            )
            return message.message_id
        
        except Exception:
            return None