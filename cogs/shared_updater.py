import os
from telegram.ext import Updater

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
updater = Updater(token=telegram_token, use_context=True)

def get_updater():
    return updater