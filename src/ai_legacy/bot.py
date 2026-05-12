"""Telegram-бот: точка входа. Только Данила как пользователь (single-user mode)."""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler as TGMessageHandler, ContextTypes, filters

from ai_legacy.config import load_settings
from ai_legacy.db import Database
from ai_legacy.few_shot import sample_examples
from ai_legacy.handler import MessageHandler
from ai_legacy.llm import LLMClient
from ai_legacy.personality import load_personality


logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, settings, handler: MessageHandler):
        self._settings = settings
        self._handler = handler

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_owner(update):
            await update.message.reply_text("Извини, я пока в режиме разработки и общаюсь только с владельцем.")
            return
        await update.message.reply_text("Привет. Я ИИ-копия. Пиши — отвечу.")

    async def about(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Я ИИ-копия владельца, обученная на его переписках и интервью. "
            "Сейчас работаю в тестовом режиме, доступна только владельцу."
        )

    async def on_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_owner(update):
            await update.message.reply_text("Сейчас в тестовом режиме, общаюсь только с владельцем.")
            return

        user_id = update.effective_user.id
        text = update.message.text
        logger.info("incoming user_id=%s text=%r", user_id, text)

        try:
            response = self._handler.handle(user_id=user_id, message=text)
        except Exception:
            logger.exception("handler failed")
            await update.message.reply_text("Что-то у меня сломалось внутри. Посмотрю позже.")
            return

        await update.message.reply_text(response)

    def _is_owner(self, update: Update) -> bool:
        return update.effective_user.id == self._settings.owner_telegram_user_id


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    settings = load_settings()

    # Инициализируем БД
    db = Database(settings.db_path)
    db.init_schema()

    # Грузим personality и few-shot
    personality = load_personality(settings.personality_dir)
    few_shot = sample_examples(settings.messages_dir, n=10)
    logger.info("loaded personality + %d few-shot examples", len(few_shot))

    # LLM-клиент (OpenAI-совместимый — по умолчанию Groq)
    llm = LLMClient(
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        base_url=settings.llm_base_url,
    )

    # Handler
    handler = MessageHandler(
        db=db, llm=llm, personality=personality,
        few_shot=few_shot, owner_name="Данила",
    )

    # Telegram
    app = Application.builder().token(settings.telegram_bot_token).build()
    bot = TelegramBot(settings=settings, handler=handler)

    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("about", bot.about))
    app.add_handler(TGMessageHandler(filters.TEXT & ~filters.COMMAND, bot.on_message))

    logger.info("bot starting")
    app.run_polling()


if __name__ == "__main__":
    main()
