import logging
from datetime import datetime, timedelta
from itertools import groupby
from random import choice
from typing import List

from bot.management.commands.notificator import notify_everybody, notify_free_students
from bot.models import ProductManager, Project, Student, TeamProject, TimeSlot, PriorityStudents

MAX_TEAM_MEMBERS = 3
CALL_TIME_MINUTES = 30
STUDENTS_LEVELS = (
    Student.BEGINNER,
    Student.BEGINNER_PLUS,
    Student.JUNIOR,
)
PROJECTS_START_DATE = "2022-01-24"
PROJECTS_END_DATE = "2022-02-05"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def find_priority_student(student: Student) -> List[Student]:
    my_pairs = []
    pairs_1 = PriorityStudents.objects.filter(student_1=student).all()
    my_pairs += [pair.student_2 for pair in pairs_1]
    pairs_2 = PriorityStudents.objects.filter(student_2=student).all()
    my_pairs += [pair.student_1 for pair in pairs_2]
    return my_pairs


def choose_slots(slots: List[TimeSlot]) -> List[TimeSlot]:
    max_slot = []
    for slot in slots:
        team_slots = [slot, ]
        student = slot.student
        my_team_slots = slots.copy()
        my_team_slots.remove(slot)
        my_pairs = find_priority_student(student)
        for team_slot in my_team_slots:
            if team_slot.student in my_pairs:
                team_slots.append(team_slot)
            if len(team_slots) == MAX_TEAM_MEMBERS:
                return team_slots
            if len(team_slots) > len(max_slot):
                max_slot = team_slots.copy()
    my_team_slots = slots.copy()
    for slot in max_slot:
        my_team_slots.remove(slot)
    for i in range(MAX_TEAM_MEMBERS - len(max_slot)):
        logger.info(i)
        new_choice = choice(my_team_slots)
        max_slot.append(new_choice)
        my_team_slots.remove(new_choice)
    return max_slot


def make_teams():
    """Распределение учеников по командам и менеджерам."""
    if not Student.objects.exists():
        return "Нет учеников, сначала необходимо зарегистрировать учеников."
    if not ProductManager.objects.exists():
        return "Нет менеджеров, сначала необходимо зарегистрировать менеджеров."

    students_count = Student.objects.count()
    pm_count = ProductManager.objects.count()
    max_teams_of_manager = students_count // MAX_TEAM_MEMBERS // pm_count

    for pm in ProductManager.objects.all():
        pm_teams_count = 0
        pm_timeslots = TimeSlot.objects.filter(
            product_manager=pm, student__isnull=True, status=TimeSlot.FREE
        )

        for pm_timeslot in pm_timeslots:
            if pm_teams_count == max_teams_of_manager:
                break

            for level in STUDENTS_LEVELS:
                if pm_teams_count == max_teams_of_manager:
                    break

                students_timeslots = TimeSlot.objects.filter(
                    time_slot=pm_timeslot.time_slot,
                    product_manager__isnull=True,
                    student__isnull=False,
                    student__level=level,
                    status=TimeSlot.FREE,
                )  # TODO: add disctinct by student?

                if students_timeslots.count() < MAX_TEAM_MEMBERS:
                    continue

                team_timeslots = choose_slots(list(students_timeslots))
                # team_timeslots = students_timeslots[:3]

                typical_project = choice(Project.objects.all())
                team_project = TeamProject.objects.create(
                    date_start=datetime.fromisoformat(PROJECTS_START_DATE),
                    date_end=datetime.fromisoformat(PROJECTS_END_DATE),
                    project=typical_project,
                )

                for slot in team_timeslots:
                    slot.product_manager = pm
                    slot.team_project = team_project
                    slot.status = TimeSlot.BUSY
                    slot.save()
                    for slot in slot.student.timeslots.filter(status=TimeSlot.FREE):
                        slot.status = TimeSlot.NON_ACTUAL
                        slot.save()

                pm_teams_count += 1
                pm_timeslot.status = TimeSlot.NON_ACTUAL
                pm_timeslot.save()
                break

    notify_everybody()
    notify_free_students(get_unallocated_students())
    return "Распределение успешно"


def cancel_distribution():
    """Отмена распределения, только для непрошедщих проектов."""

    busy_timeslots = TimeSlot.objects.filter(
        status=TimeSlot.BUSY,
        team_project__date_end__gte=datetime.now(),
    )
    if not busy_timeslots.exists():
        return "Не найдено временных слотов!"

    for slot in busy_timeslots:
        slot.product_manager = None
        slot.team_project = None
        slot.status = TimeSlot.FREE
        slot.save()

    non_actual_timeslots = TimeSlot.objects.filter(
        status=TimeSlot.NON_ACTUAL,
    )

    for slot in non_actual_timeslots:
        slot.status = TimeSlot.FREE
        slot.save()

    return "Отмена распределения выполнена успешно"


def get_unallocated_students():
    """Выборка нераспределенных по ПМам и группам учеников,
    т.е. тех, у которых все таймслоты имеют статус 'FREE'."""

    students = Student.objects.all()
    unallocated_students = []
    for student in students:
        timeslot_status_dict = student.timeslots.all().values("status")
        if all(item["status"] == TimeSlot.FREE for item in timeslot_status_dict):
            unallocated_students.append(student)

    return unallocated_students


def _timestamps_by_range(time_start, time_end):
    time_delta = timedelta(minutes=CALL_TIME_MINUTES)
    timestamps = []

    while time_start <= time_end:
        timestamps.append(time_start.time())
        time_start += time_delta

    return timestamps


def _create_timeslot(time_slot=None, student=None, pm=None, team_project=None):
    """Создает записи таймслота для заданого времени."""

    return TimeSlot.objects.get_or_create(
        time_slot=time_slot,
        student=student,
        product_manager=pm,
        team_project=team_project,
    )


def make_timeslots(time_start, time_end, tg_id, project=None):
    """Создание таймслотов для ученика или менеджера."""

    try:
        pm = ProductManager.objects.get(tg_id=tg_id)
    except ProductManager.DoesNotExist:
        pm = None

    try:
        student = Student.objects.get(tg_id=tg_id)
    except Student.DoesNotExist:
        student = None

    time_stamps = _timestamps_by_range(time_start, time_end)

    for time_stamp in time_stamps:
        _create_timeslot(
            time_slot=time_stamp, pm=pm, student=student, team_project=project
        )


def get_teams():
    """Возвращает список словарей команд
    сгруппированных по менеджеру и времени созвона."""

    busy_timeslots = TimeSlot.objects.filter(status=TimeSlot.BUSY).values(
        "id", "time_slot", "product_manager__id", "student__id"
    )
    sort_func = lambda timeslot: (
        timeslot["product_manager__id"],
        timeslot["time_slot"],
    )

    busy_timeslots_sorted = sorted(busy_timeslots, key=sort_func)
    teams = groupby(busy_timeslots_sorted, key=sort_func)
    teams_list = []

    for keys, timeslot_values in teams:
        pm_id, time = keys
        teams_list.append(
            {
                "pm_id": pm_id,
                "time": time,
                "time_slot_vals": list(timeslot_values),
            }
        )

    return teams_list
