import asyncio

from loguru import logger
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

from channels.abstract_channel import AbstractChannel
from config import TELEGRAM_BOT_TOKEN
from events.event_types import EventType
from events.eventbus import EventBus
from config import ALLOWED_TELEGRAM_USER


class TelegramChannel(AbstractChannel):
    def __init__(
        self,
        event_bus: EventBus,
    ):
        super().__init__()
        self.event_bus = event_bus
        self.app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_message)
        )
        self.chat_id = None

    async def _on_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.type != "private":
            logger.error("Private chat only")
            return

        message = update.message.text
        self.chat_id = str(update.effective_chat.id)

        logger.info(
            f"Received message: {message} from chat {self.chat_id} {update.effective_user.id}"
        )

        if update.effective_user.username.lower() != ALLOWED_TELEGRAM_USER.lower():
            logger.error(f"User {ALLOWED_TELEGRAM_USER} not allowed")
            return

        await self.event_bus.publish(EventType.PROCESS_MESSAGE, user_input=message)

    async def start(self):
        logger.info("Telegram bot started...")
        try:
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            self.event_bus.publish(EventType.SHUTDOWN)

    async def send(self, message: str):
        await self.app.bot.send_message(
            chat_id=self.chat_id,
            text=message,
            parse_mode="Markdown",
        )
