from enum import Enum, auto
from telegram import Bot, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)


class States(Enum):
    START = auto()
    START_PM = auto()
    START_STUDENT = auto()


def send_first_step_pm(update: Update, context: CallbackContext) -> States:
    update.effective_user.send_message(
        text="Добро пожаловать PM.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def get_pm_conversation():
    return ConversationHandler(
        entry_points=[
            CommandHandler("send_first_step_pm", send_first_step_pm),
        ],
        states={
            "send_first_step_pm": [
                MessageHandler(Filters.text & ~
                               Filters.command, send_first_step_pm),
            ],
            # States.START_PM: [
            #     MessageHandler(Filters.text & ~
            #                    Filters.command, first_step),
            # ],
            # States.START_STUDENT: [
            #     MessageHandler(Filters.text & ~
            #                    Filters.command, first_step),
            # ],
        },
        fallbacks=[
            # CommandHandler("cancel", cancel),
        ],
    )
