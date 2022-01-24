import logging
from datetime import datetime, timedelta

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ParseMode,
                      ReplyKeyboardMarkup, Update)
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def keyboard_row_divider(full_list, row_width=2):
    """Divide list into rows for keyboard"""
    for i in range(0, len(full_list), row_width):
        yield full_list[i: i + row_width]


def get_time_period_key(start_time, end_time):
    return f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"


def get_working_time_string(start_time, end_time):
    return f'⏰ Время работы: `{get_time_period_key(start_time, end_time)}`'


def save_time_period_pm(context, time_key, start_time, end_time):
    time_period = context.user_data["time_period"]

    if time_key in time_period:
        time_period.pop(time_key)

    time_period[get_time_period_key(start_time, end_time)] = [
        start_time, end_time]


def delete_time_period_pm(context, time_key):
    time_period = context.user_data["time_period"]

    if time_key in time_period:
        time_period.pop(time_key)


def get_array_time_period(context):
    time_period = context.user_data["time_period"]
    list_period = []

    for period_key in sorted(time_period.keys()):
        list_period.append(period_key)

    list_period.append("Добавить")

    return list_period


def get_inline_kb_for_change_time():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('+',
                                     callback_data='TIME_+'),
                InlineKeyboardButton('-',
                                     callback_data='TIME_-'),
                InlineKeyboardButton('+',
                                     callback_data='TIME_+2'),
                InlineKeyboardButton('-',
                                     callback_data='TIME_-2'),
            ],
            [
                InlineKeyboardButton('📄 Сохранить',
                                     callback_data='TIME_SAVE')],
        ]
    )


def show_period_pm(update: Update, context: CallbackContext):
    logger.info("update.message.text: %s", update.effective_message.text)

    if "time_period" not in context.user_data:
        context.user_data["time_period"] = dict()

    reply_keyboard = list(keyboard_row_divider(
        get_array_time_period(context), 1))

    markup_key = ReplyKeyboardMarkup(reply_keyboard,
                                     one_time_keyboard=True,
                                     resize_keyboard=True)

    update.effective_message.reply_text(
        'Ваш список рабочих периодов.',
        reply_markup=markup_key,)

    return "change_or_add_period_pm"


def change_or_add_period_pm(update: Update, context: CallbackContext):
    logger.info("update.message.text: %s", update.message.text)

    if update.message.text == "Добавить":
        reply_keyboard = list(keyboard_row_divider(
            ['Утро', 'Вечер'], 2))

        markup_key = ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=True,
                                         resize_keyboard=True)
        update.message.reply_text(
            'На какое время суток создать период?',
            reply_markup=markup_key,)

        return "add_period_pm"
    else:
        context.user_data['time_key'] = update.message.text

        reply_keyboard = list(keyboard_row_divider(
            ['Изменить', 'Удалить']))

        markup_key = ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=True,
                                         resize_keyboard=True)
        update.message.reply_text(
            'Что Вы хотите сделать с периодом?',
            reply_markup=markup_key,)

        return "question_change_or_delete_period"


def add_period_pm(update: Update, context: CallbackContext):
    logger.info("update.message.text: %s", update.message.text)
    user = update.effective_user

    if update.message.text == "Утро":
        context.user_data['start_time'] = datetime(1970, 1, 1, 10, 0, 0)
        context.user_data['end_time'] = datetime(1970, 1, 1, 12, 0, 0)
        start_time = context.user_data['start_time']
        end_time = context.user_data['end_time']
    else:
        context.user_data['start_time'] = datetime(1970, 1, 1, 18, 0, 0)
        context.user_data['end_time'] = datetime(1970, 1, 1, 20, 0, 0)
        start_time = context.user_data['start_time']
        end_time = context.user_data['end_time']

    context.user_data['time_key'] = get_time_period_key(start_time, end_time)

    update.message.reply_text(
        get_working_time_string(start_time, end_time),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_inline_kb_for_change_time()
    )

    return "inline_button_change_time"


def question_change_or_delete_period(update: Update, context: CallbackContext):
    logger.info("update.message.text: %s", update.message.text)
    user = update.effective_user

    if update.message.text == "Изменить":
        return edit_period_pm(update, context)
    elif update.message.text == "Удалить":
        delete_time_period_pm(context, context.user_data['time_key'])
        return show_period_pm(update, context)


def edit_period_pm(update: Update, context: CallbackContext):
    logger.info("update.message.text: %s", update.message.text)

    period_time = context.user_data['time_key'].split("-")

    try:
        start_hours, start_minutes = map(int, period_time[0].split(':'))
        end_hours, end_minutes = map(int, period_time[1].split(':'))

        context.user_data['start_time'] = datetime(
            1970, 1, 1, start_hours, start_minutes, 0)
        context.user_data['end_time'] = datetime(
            1970, 1, 1, end_hours, end_minutes, 0)
        start_time = context.user_data['start_time']
        end_time = context.user_data['end_time']

        update.message.reply_text(
            get_working_time_string(start_time, end_time),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=get_inline_kb_for_change_time()
        )

        return "inline_button_change_time"
    except:
        pass

    return show_period_pm(update, context)


def inline_button_change_time(update: Update, context: CallbackContext):
    bot = update.effective_message.bot
    query = update.callback_query

    start_time = context.user_data['start_time']
    end_time = context.user_data['end_time']

    if query.data == 'TIME_+':
        start_time += timedelta(minutes=30)
    elif query.data == 'TIME_-':
        start_time -= timedelta(minutes=30)
    elif query.data == 'TIME_+2':
        end_time += timedelta(minutes=30)
    elif query.data == 'TIME_-2':
        end_time -= timedelta(minutes=30)
    elif query.data == 'TIME_SAVE':
        save_time_period_pm(
            context,
            context.user_data['time_key'],
            start_time,
            end_time)
        return show_period_pm(update, context)

    context.user_data['start_time'] = start_time
    context.user_data['end_time'] = end_time

    context.bot.edit_message_text(
        text=get_working_time_string(start_time, end_time),
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_inline_kb_for_change_time(),
    )


pm_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        show_period_pm, pattern="^show_period_pm")],
    states={
        "show_period_pm": [MessageHandler(Filters.text & ~Filters.command, show_period_pm)],
        "change_or_add_period_pm": [MessageHandler(Filters.text & ~Filters.command, change_or_add_period_pm)],
        "add_period_pm": [MessageHandler(Filters.text & ~Filters.command, add_period_pm)],
        "edit_period_pm": [MessageHandler(Filters.text & ~Filters.command, edit_period_pm)],
        "inline_button_change_time": [CallbackQueryHandler(inline_button_change_time, pattern='^TIME_')],
        "question_change_or_delete_period": [MessageHandler(Filters.text & ~Filters.command, question_change_or_delete_period)],
    },
    fallbacks=[
        # CommandHandler('cancel', cancel)
    ],
)


# pm_conv = ConversationHandler(
#     entry_points=[
#         CallbackQueryHandler(
#             select_time, pattern="^" + str(Consts.SELECT_TIME.value) + "$"
#         )
#     ],
#     states={
#         States.SELECT_TIME: [
#             CallbackQueryHandler(time_handler, pattern=f"^{CALLBACK_NAME}"),
#             CallbackQueryHandler(
#                 cancel_all, pattern=f"^{Consts.CHOSE_NOTHING.value}"),
#         ],
#     },
#     fallbacks=[
#         CallbackQueryHandler(
#             finer, pattern="^" + str(Consts.END_SELECTING.value) + "$"
#         ),
#     ],
#     map_to_parent={
#         # End everything!
#         ConversationHandler.END: ConversationHandler.END,
#     },
# )
