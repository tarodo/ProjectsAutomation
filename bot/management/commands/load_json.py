import datetime
import json

from django.core.management.base import BaseCommand

from bot.models import Student, ProductManager, TimeSlot
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s :: %(levelname)s :: %(name)10s :: %(funcName)12s :: %(message)s",
)
logger = logging.getLogger("load_json")


class StudentModel(BaseModel):
    name: str
    level: str
    tg_username: str
    discord_username: str
    is_far_east: bool


class ManagerModel(BaseModel):
    name: str
    tg_username: str


class ManagerTimeSlotModel(BaseModel):
    tg_username: str
    timeslot: str


class StudentTimeSlotModel(ManagerTimeSlotModel):
    pass


def save_student(student: dict):
    """Save one student to DB"""
    student = StudentModel.parse_obj(student)
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


def save_manager(pm: dict):
    """Save one student to DB"""
    manager = ManagerModel.parse_obj(pm)

    new_manager = ProductManager(
        name=manager.name,
        tg_username=manager.tg_username
    )
    new_manager.save()


def save_manager_timeslot(pm_slot: dict):
    """Save timeslot for manager in DB"""
    slot = ManagerTimeSlotModel.parse_obj(pm_slot)
    manager = ProductManager.objects.get(tg_username=slot.tg_username)
    start_time = datetime.datetime.strptime(slot.timeslot, '%H:%M')
    return TimeSlot.objects.get_or_create(
        time_slot=start_time,
        student=None,
        product_manager=manager,
        team_project=None,
    )


def save_student_timeslot(student_slot: dict):
    """Save timeslot for student in DB"""
    slot = StudentTimeSlotModel.parse_obj(student_slot)
    student = Student.objects.get(tg_username=slot.tg_username)
    start_time = datetime.datetime.strptime(slot.timeslot, '%H:%M')
    return TimeSlot.objects.get_or_create(
        time_slot=start_time,
        student=student,
        product_manager=None,
        team_project=None,
    )


def load_json(json_path: str, save_func: callable):
    with open(json_path, "r") as read_file:
        json_data = json.load(read_file)

    err_cnt = 0
    for elem in json_data:
        try:
            save_func(elem)
        except ValidationError:
            err_cnt += 1
        except ProductManager.DoesNotExist:
            err_cnt += 1

    if err_cnt > 0:
        logger.error(f"Errors in data: {err_cnt}")
    if err_cnt == 0:
        logger.info(f"All entities from {json_path}({len(json_data)}) were uploaded")
    return True


class Command(BaseCommand):
    """Load data"""

    help = "Телеграм-бот"

    def handle(self, *args, **options):
        if options["table"] == "student":
            load_json(options["json"], save_student)
        if options["table"] == "pm":
            load_json(options["json"], save_manager)
        if options["table"] == "pm_slot":
            load_json(options["json"], save_manager_timeslot)
        if options["table"] == "student_slot":
            load_json(options["json"], save_student_timeslot)

    def add_arguments(self, parser):
        parser.add_argument(
            '-j',
            '--json',
            action='store',
            help='Путь до JSON файла'
        )
        parser.add_argument(
            '-t',
            '--table',
            action="store",
            help="Таблица назначения",
            default="student"
        )