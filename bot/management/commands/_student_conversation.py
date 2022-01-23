import datetime
import logging
from datetime import timedelta
from enum import Enum, auto

from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update,
)
from telegram.ext import (
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext,
)

from bot.models import TimeSlot, Student
from bot.utils.timeslots_utils import make_timeslots, CALL_TIME_MINUTES

logger = logging.getLogger("student")


class States(Enum):
    SELECT_TIME = auto()


class Consts(Enum):
    SELECT_TIME = "select_date"
    END_SELECTING = "end_selecting"
    CHOSE_NOTHING = "cancel all"


CALLBACK_NAME = "CHOOSE_TIME"
SEPARATOR = "::"
LIKE_ICON = "\u2705"


def create_callback_time(time):
    """Create the callback time associated to each button"""
    return f"{CALLBACK_NAME}{SEPARATOR}{time}"


def separate_callback_data(data: str):
    return data.split(SEPARATOR)


def keyboard_row_divider(full_list, row_width=2):
    """Divide list into rows for keyboard"""
    for i in range(0, len(full_list), row_width):
        yield full_list[i : i + row_width]


def keyboard_generator(context, keys=None):
    context.user_data["time_keys"] = keys
    buttons = [
        InlineKeyboardButton(text=time_el, callback_data=create_callback_time(time_el))
        for time_el in keys
    ]
    key_buttons = list(keyboard_row_divider(buttons, 3))
    key_buttons.append(
        [
            InlineKeyboardButton(
                text="Отменить все", callback_data=Consts.CHOSE_NOTHING.value
            )
        ]
    )
    key_buttons.append(
        [
            InlineKeyboardButton(
                text="Закончить", callback_data=Consts.END_SELECTING.value
            )
        ]
    )

    return InlineKeyboardMarkup(key_buttons)


def select_time(update: Update, context: CallbackContext):
    empty_slots = (
        TimeSlot.objects.filter(
            product_manager__isnull=False, student__isnull=True, status=TimeSlot.FREE
        )
        .values("time_slot")
        .distinct()
    )
    user_id = update.callback_query.from_user.id
    student_time = []
    try:
        student = Student.objects.get(tg_id=user_id)
        logger.info(student)
        student_slots = student.timeslots.values("time_slot").distinct()
        student_time = [slot["time_slot"].strftime("%H:%M") for slot in student_slots]
    except Student.DoesNotExist:
        pass

    empty_time = [slot["time_slot"].strftime("%H:%M") for slot in empty_slots]
    prepare_time = []
    for time in empty_time:
        new_time = time
        if time in student_time:
            new_time = f"{time}{LIKE_ICON}"
        prepare_time.append(new_time)

    keyboard = keyboard_generator(context, prepare_time)

    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text="Выберите удобное для Вас время", reply_markup=keyboard
    )

    return States.SELECT_TIME


def time_handler(update, context):
    query = update.callback_query
    _, choosing_time = separate_callback_data(query.data)
    keys = context.user_data.get("time_keys")
    new_keys = []
    for key in keys:
        if key == choosing_time:
            if key.endswith(f"{LIKE_ICON}"):
                new_keys.append(key.replace(f"{LIKE_ICON}", ""))
            else:
                new_keys.append(f"{key}{LIKE_ICON}")
        else:
            new_keys.append(key)

    update.callback_query.answer()
    context.bot.edit_message_text(
        text=query.message.text,
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=keyboard_generator(context, new_keys),
    )

    return States.SELECT_TIME


def cancel_all(update, context):
    query = update.callback_query
    keys = context.user_data.get("time_keys")
    new_keys = []
    for key in keys:
        if key.endswith(f"{LIKE_ICON}"):
            new_keys.append(key.replace(f"{LIKE_ICON}", ""))
        else:
            new_keys.append(key)

    update.callback_query.answer()
    if keys != new_keys:
        context.bot.edit_message_text(
            text=query.message.text,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=keyboard_generator(context, new_keys),
        )

    return States.SELECT_TIME


def collect_time(context: CallbackContext):
    keys = context.user_data.get("time_keys")
    result_keys = [
        key.replace(f"{LIKE_ICON}", "") for key in keys if key.endswith(f"{LIKE_ICON}")
    ]
    return result_keys


def clear_time(user_id):
    student = Student.objects.get(tg_id=user_id)
    student.timeslots.all().delete()


def save_time(user_id, time_keys):
    clear_time(user_id)
    time_delta = timedelta(minutes=CALL_TIME_MINUTES - 1)
    for key in time_keys:
        start_time = datetime.datetime.strptime(key, "%H:%M")
        fin_time = start_time + time_delta
        make_timeslots(start_time, fin_time, user_id)


def finer(update: Update, context: CallbackContext):
    update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    student_time = collect_time(context)
    save_time(user_id, student_time)
    text = "Вы отменили свое участие в проекте"
    if student_time:
        text = f"Вы выбрали время: {', '.join(student_time)}"
    update.callback_query.edit_message_text(text=text)

    return ConversationHandler.END


student_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            select_time, pattern="^" + str(Consts.SELECT_TIME.value) + "$"
        )
    ],
    states={
        States.SELECT_TIME: [
            CallbackQueryHandler(time_handler, pattern=f"^{CALLBACK_NAME}"),
            CallbackQueryHandler(cancel_all, pattern=f"^{Consts.CHOSE_NOTHING.value}"),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(
            finer, pattern="^" + str(Consts.END_SELECTING.value) + "$"
        ),
    ],
    map_to_parent={
        # End everything!
        ConversationHandler.END: ConversationHandler.END,
    },
)
