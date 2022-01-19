import logging
import os
from enum import Enum, auto

from django.core.management.base import BaseCommand
from telegram import Bot, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)
from telegram.utils.request import Request
from bot.models import ProductManager

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

request = Request(connect_timeout=0.5, read_timeout=1.0)
bot = Bot(
    request=request,
    token=TELEGRAM_TOKEN,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class States(Enum):
    START = auto()


def keyboard_row_divider(full_list, row_width=2):
    """Divide list into rows for keyboard"""
    for i in range(0, len(full_list), row_width):
        yield full_list[i: i + row_width]


def send_first_question(update: Update, context: CallbackContext) -> States:
    buttons = ["Список проектов", "Список ПМ'ов", "Список учеников"]
    reply_keyboard = list(keyboard_row_divider(buttons))
    update.message.reply_text(
        "Вот ду ю вонт?:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    return States.START


def start(update: Update, context: CallbackContext) -> States:
    user = update.message.from_user
    update.message.reply_text(
        f"Привет, {user.full_name if user.full_name else user.username}")
    logger.info(
        f"User {user.first_name} :: {user.id} started the conversation.")

    new_pm, _ = ProductManager.objects.get_or_create(
        tg_id=user.id,
        tg_username=user.username,
        name=user.full_name,
        surname=user.first_name)

    return send_first_question(update, context)


def first_step(update: Update, context: CallbackContext) -> States:
    update.effective_user.send_message(
        text="На этом мои полномочия все( ", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def cancel(update: Update, _) -> int:
    """Cancel and end the conversation."""
    user = update.message.from_user
    logger.info(
        f"User {user.first_name} :: {user.id} canceled the conversation.")
    update.message.reply_text(
        "Всего доброго!", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


class Command(BaseCommand):
    """Start the bot."""

    help = "Телеграм-бот"

    def handle(self, *args, **options):
        updater = Updater(token=TELEGRAM_TOKEN)
        dispatcher = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("start", start),
            ],
            states={
                States.START: [
                    MessageHandler(Filters.text & ~
                                   Filters.command, first_step),
                ],
            },
            fallbacks=[
                CommandHandler("cancel", cancel),
            ],
        )

        dispatcher.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()
