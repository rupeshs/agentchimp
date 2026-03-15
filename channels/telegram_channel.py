import asyncio
import random
import string
from json import dump, load

from loguru import logger
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from channels.abstract_channel import AbstractChannel
from config import TELEGRAM_BOT_TOKEN
from events.event_types import EventType
from events.eventbus import EventBus


class TelegramChannel(AbstractChannel):
    def __init__(
        self,
        event_bus: EventBus,
    ):
        super().__init__()
        self.event_bus = event_bus
        self.app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        self.chat_id = None
        self.allowed_user_id = None
        self.pairing_code = self._generate_pairing_code()
        self._load_paired_user()
        logger.info(f"Pairing code for your Telegram bot: {self.pairing_code}")
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_message)
        )
        self.app.add_handler(CommandHandler("pair", self._pair))

    def _load_paired_user(self):
        try:
            with open("paired_user.json", "r") as f:
                data = load(f)
                self.allowed_user_id = data.get("allowed_user_id")
        except FileNotFoundError:
            self.allowed_user_id = None

    def _save_paired_user(self):
        if self.allowed_user_id is not None:
            with open("paired_user.json", "w") as f:
                dump({"allowed_user_id": self.allowed_user_id}, f)

    def _generate_pairing_code(self, length=6):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

    async def _pair(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        text = update.message.text.strip()
        parts = text.split()
        if len(parts) != 2:
            await update.message.reply_text("Usage: /pair <code>")
            return

        code = parts[1].upper()
        if code != self.pairing_code:
            await update.message.reply_text("Invalid pairing code.")
            return

        self.allowed_user_id = user.id
        self.pairing_code = None
        logger.info(f"User {user.id} paired successfully")
        self._save_paired_user()
        await update.message.reply_text(
            f"Paired successfully! User ID {user.id} authorized."
        )

    async def _on_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.type != "private":
            logger.error("Private chat only")
            return
        message = update.message.text
        logger.info(
            f"Received message: {message} from chat {self.chat_id} {update.effective_user.id}"
        )
        if self.allowed_user_id:
            self.chat_id = str(update.effective_chat.id)
            await self.event_bus.publish(EventType.PROCESS_MESSAGE, user_input=message)
        else:
            logger.error("User is not authorized")
            await update.message.reply_text(
                "You are not authorized to chat with me\n To pair send /pair <pairing_code> from bot, check Agent Chimp log for pairing code"
            )

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
