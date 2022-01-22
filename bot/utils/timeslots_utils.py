from datetime import datetime, timedelta
from sqlite3 import Timestamp
from bot.models import ProductManager, Student, TimeSlot

CALL_TIME_MINUTES = 30


def make_teams():
    """Распределение учеников по командам и менеджерам."""

    MAX_TEAM_MEMBERS = 3
    MAX_MANAGER_TEAMS = (
        Student.objects.count() // MAX_TEAM_MEMBERS // ProductManager.objects.count()
    )

    for pm in ProductManager.objects.all():
        pm_teams_count = 0
        pm_timeslots = TimeSlot.objects.filter(
            product_manager=pm, student__isnull=True, status=TimeSlot.FREE
        )
        for pm_timeslot in pm_timeslots:
            if pm_teams_count == MAX_MANAGER_TEAMS:
                break

            for level in (Student.BEGINNER, Student.BEGINNER_PLUS, Student.JUNIOR):
                if pm_teams_count == MAX_MANAGER_TEAMS:
                    break

                students_timeslots = TimeSlot.objects.filter(
                    product_manager__isnull=True,
                    student__isnull=False,
                    student__level=level,
                    time_slot=pm_timeslot.time_slot,
                    status=TimeSlot.FREE,
                )  # TODO: add disctinct by student?

                if students_timeslots.count() < MAX_TEAM_MEMBERS:
                    continue

                team_timeslots = students_timeslots[:3]
                for slot in team_timeslots:
                    slot.product_manager = pm
                    slot.status = TimeSlot.BUSY
                    slot.save()
                    for slot in slot.student.timeslots.filter(status=TimeSlot.FREE):
                        slot.status = TimeSlot.NON_ACTUAL
                        slot.save()

                pm_teams_count += 1
                pm_timeslot.status = TimeSlot.NON_ACTUAL
                pm_timeslot.save()
                break


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
