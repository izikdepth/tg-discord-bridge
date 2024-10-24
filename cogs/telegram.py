import os
import requests
from telegram.ext import MessageHandler, Filters
from telegram import ParseMode
from dotenv import load_dotenv
from cogs.shared_updater import get_updater
from telegram.utils.helpers import escape_markdown

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

class TelegramBridge:
    def __init__(self, discord_bot):
        self.bot = discord_bot
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.tg_chat_id = int(os.getenv("TELEGRAM_CHAT"))
        self.discord_channel_id = int(os.getenv("DISCORD_TGCHAT"))
        self.discord_bot_token = os.getenv("DDLN_BOT")
        self.tg_updater = get_updater()
        self.message_map = {}

        print("Telegram Bridge initialized with:")
        print(f"Telegram Chat ID: {self.tg_chat_id}")

        # Start Telegram listener
        self.start_telegram_listener()

    def start_telegram_listener(self):
        dp = self.tg_updater.dispatcher
        dp.add_handler(MessageHandler(Filters.chat(self.tg_chat_id) & Filters.text, self.handle_telegram_message))
        dp.add_error_handler(self.error_handler)
        self.tg_updater.start_polling()
        print("Telegram listener started")

    def error_handler(self, update, context):
        print(f"Error: {context.error}")
        
    def escape_markdown_v2(self, text):
        escape_chars = r'\*_`\[\]()~>#+-=|{}.!'
        return ''.join(['\\' + char if char in escape_chars else char for char in text])

    def handle_telegram_message(self, update, context):
        tg_message = update.message
        author = tg_message.from_user.full_name
        text = tg_message.text or ''

        # Ignore attachments
        if tg_message.photo or tg_message.video or tg_message.document:
            return

        discord_message_id = self.send_message_to_discord(author, text)
        self.message_map[tg_message.message_id] = discord_message_id

    def send_message_to_discord(self, author, text):
        url = f"https://discord.com/api/channels/{self.discord_channel_id}/messages"
        headers = {
            "Authorization": f"Bot {self.discord_bot_token}",
            "Content-Type": "application/json"
        }
        data = {
            "content": None,
            "embeds": [{
                "description": text,
                "color": 0x3498db,
                "author": {
                    "name": author,
                    "icon_url": "https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg"
                }
            }]
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json().get('id')
        except requests.exceptions.RequestException as e:
            print(f"Error sending message to Discord: {e}")
            if e.response is not None:
                print(f"Response: {e.response.text}")
            return None


    def send_message_to_telegram(self, author, text, original_message_id=None):
        formatted_text = f"<b>{escape_markdown(author)}</b>\n{escape_markdown(text)}"
        message = self.tg_updater.bot.send_message(chat_id=self.tg_chat_id, text=formatted_text, parse_mode=ParseMode.HTML, reply_to_message_id=original_message_id)
        return message.message_id