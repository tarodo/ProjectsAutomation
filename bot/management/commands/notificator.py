import logging
import os

from bot.models import TeamProject, Student, TimeSlot
from telegram.utils.request import Request
from telegram import Bot, ParseMode

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

request = Request(connect_timeout=0.5, read_timeout=1.0)
bot = Bot(
    request=request,
    token=TELEGRAM_TOKEN,
)


def escape_characters(text: str) -> str:
    """Screen characters for Markdown V2"""
    text = text.replace("\\", "")
    characters = [".", "+", "(", ")", "-", "!", "=", "_"]
    for character in characters:
        text = text.replace(character, f"\{character}")
    return text


def notify_everybody():
    projects = TeamProject.objects.all()
    for project in projects:
        timeslots = project.timeslots.all()
        team = []
        pm = None
        call_time = ""
        for timeslot in timeslots:
            team.append(timeslot.student)
            pm = timeslot.product_manager
            call_time = timeslot.time_slot.strftime("%H:%M")

        start_date = project.date_start.strftime("%d.%m.%Y")
        fin_date = project.date_end.strftime("%d.%m.%Y")
        project_name = project.project.name
        team_txt = "\n".join([f"{teammate}" for teammate in team])
        if pm:
            user_id = pm.tg_id
            if user_id:
                text = (
                    f"Поздравляем! Для вас сформировалась группа студентов\n"
                    f"Проект: *{project_name}*\n"
                    f"Даты: *{start_date} - {fin_date}*\n"
                    f"Команда: \n*{team_txt}*\n"
                    f"Созвон в: *{call_time}*"
                )
                logger.error(f"{user_id=} :: {text=}")
                bot.send_message(
                    chat_id=user_id,
                    text=escape_characters(text),
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
        for student in team:
            if student.tg_id:
                my_team = team.copy()
                my_team.remove(student)
                user_id = student.tg_id
                team_txt = "\n".join([f"{teammate}" for teammate in my_team])
                text = (
                    f"На неделе с *{start_date} - {fin_date}* вы участвуете в команде с:\n*{team_txt}*\n"
                    f"Ваш ПМ: *{pm}*\n"
                    f"Проект: *{project_name}*\n"
                    f"Созвон в: *{call_time}*"
                )
                logger.info(f"{user_id=} :: {text=}")
                bot.send_message(
                    chat_id=user_id,
                    text=escape_characters(text),
                    parse_mode=ParseMode.MARKDOWN_V2,
                )


def notify_free_students(free_students):
    for student in free_students:
        if student.tg_id:
            user_id = student.tg_id
            empty_slots = (
                TimeSlot.objects.filter(
                    product_manager__isnull=False,
                    student__isnull=True,
                    status=TimeSlot.FREE,
                )
                .values("time_slot")
                .distinct()
            )
            empty_time = [slot["time_slot"].strftime("%H:%M") for slot in empty_slots]
            text = (
                f"*{student.name}*, к сожалению на выбранные вами слоты группы не нашлось\n"
                f"Есть слоты на *{', '.join(empty_time)}*\n"
                f"Если какой-то из них устраивает добавьте его в список возможны /start\n"
                f"Спасибо"
            )
            bot.send_message(
                chat_id=user_id,
                text=escape_characters(text),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            logger.info(student)
