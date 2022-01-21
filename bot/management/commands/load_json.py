import json

from django.core.management.base import BaseCommand

from bot.models import Student
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s :: %(levelname)s :: %(name)10s :: %(funcName)12s :: %(message)s",
)
logger = logging.getLogger("load_json")


class Model(BaseModel):
    name: str
    level: str
    tg_username: str
    discord_username: str
    is_far_east: bool


def save_student(student: dict):
    """Save one student to DB"""
    student = Model.parse_obj(student)
    if student.level == "novice":
        student.level = Student.BEGINNER
    elif student.level == "novice+":
        student.level = Student.BEGINNER_PLUS
    else:
        student.level = Student.JUNIOR

    new_student = Student(
        tg_username=student.tg_username,
        name=student.name,
        level=student.level,
        discord_username=student.discord_username,
        is_far_east=student.is_far_east
    )
    new_student.save()


def load_students(json_path: str) -> bool:
    """Load JSON file to DB"""

    with open(json_path, "r") as read_file:
        students = json.load(read_file)

    err_cnt = 0
    for student in students:
        try:
            save_student(student)
        except ValidationError:
            err_cnt += 1

    if err_cnt > 0:
        logger.error(f"Errors in data: {err_cnt}")
    if err_cnt == 0:
        logger.info(f"All students({len(students)}) were uploaded")
    return True


class Command(BaseCommand):
    """Load data"""

    help = "Телеграм-бот"

    def handle(self, *args, **options):

        load_students(options["json"])

    def add_arguments(self, parser):
        parser.add_argument(
            '-j',
            '--json',
            action='store',
            help='Путь до JSON файла'
        )