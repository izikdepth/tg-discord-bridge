import os
import asyncio
from telegram.ext import ApplicationBuilder
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SafeRequest(HTTPXRequest):
    def __init__(self, token, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = token

    async def _request_wrapper(self, *args, **kwargs):
        try:
            return await super()._request_wrapper(*args, **kwargs)
        except Exception as e:
            # Replace the token in the exception message
            if self.token in str(e):
                e.args = tuple(
                    arg.replace(self.token, "[TOKEN REDACTED]") if isinstance(arg, str) else arg
                    for arg in e.args
                )
            raise


class TelegramUpdater:
    def __init__(self):
        self._application = None

    def get_application(self):
        if self._application is None:
            telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if not telegram_token:
                raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables.")

            # Use SafeRequest for the application instance
            request = SafeRequest(token=telegram_token)

            # Build the application with the custom request
            self._application = ApplicationBuilder().token(telegram_token).request(request).build()

        return self._application

    async def start_polling(self):
        """Starts the polling process for the Telegram bot."""
        print("Starting Telegram bot polling...")
        app = self.get_application()
        try:
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
        except Exception as e:
            print(f"Error starting Telegram polling: {e}")

    async def stop(self):
        """Stops the Telegram bot."""
        if self._application:
            await self._application.updater.stop()
            await self._application.stop()
            await self._application.shutdown()


# Main event loop runner
async def main():
    telegram_updater = TelegramUpdater()

    try:
        # Start Telegram bot
        await telegram_updater.start_polling()

        # Keep the event loop running for other tasks
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("Shutting down gracefully...")
        await telegram_updater.stop()


if __name__ == "__main__":
    asyncio.run(main())