from datetime import datetime, timedelta
from random import choice

from bot.models import Participant, Project, TeamProject, TimeSlot

MAX_TEAM_MEMBERS = 3
CALL_TIME_MINUTES = 30
STUDENTS_LEVELS = (
    Participant.BEGINNER,
    Participant.BEGINNER_PLUS,
    Participant.JUNIOR,
)
PROJECTS_START_DATE = "2022-01-30"
PROJECTS_END_DATE = "2022-02-07"


def make_teams():
    """Распределение учеников по командам и менеджерам."""
    # TODO: задавать даты проекта через аргументы
    if not TimeSlot.objects.filter(participant__role=Participant.STUDENT).exists():
        return "Нет учеников, сначала необходимо зарегистрировать учеников."
    if not TimeSlot.objects.filter(
        participant__role=Participant.PRODUCT_MANAGER
    ).exists():
        return "Нет менеджеров, сначала необходимо зарегистрировать менеджеров."

    students_count = Participant.objects.filter(role=Participant.STUDENT).count()
    pm_count = Participant.objects.filter(role=Participant.PRODUCT_MANAGER).count()
    max_teams_of_manager = students_count // MAX_TEAM_MEMBERS // pm_count
    if max_teams_of_manager == 0:
        max_teams_of_manager = 1

    for pm in Participant.objects.filter(role=Participant.PRODUCT_MANAGER):
        pm_teams_count = 0
        pm_timeslots = TimeSlot.objects.filter(
            participant=pm,
            team_project=None,
        )

        for pm_timeslot in pm_timeslots:
            if pm_teams_count == max_teams_of_manager:
                break

            for level in STUDENTS_LEVELS:
                if pm_teams_count == max_teams_of_manager:
                    break

                free_students_timeslots = TimeSlot.objects.filter(
                    time_slot=pm_timeslot.time_slot,
                    participant__role=Participant.STUDENT,
                    participant__level=level,
                    team_project=None,
                ).filter(participant__in=get_unallocated_students_optimized())

                if free_students_timeslots.count() < MAX_TEAM_MEMBERS:
                    continue

                team_timeslots = free_students_timeslots[:3]

                typical_project = choice(Project.objects.all())
                team_project = TeamProject.objects.create(
                    date_start=datetime.fromisoformat(PROJECTS_START_DATE),
                    date_end=datetime.fromisoformat(PROJECTS_END_DATE),
                    project=typical_project,
                )

                for slot in team_timeslots:
                    slot.team_project = team_project
                    slot.save()

                pm_timeslot.team_project = team_project
                pm_timeslot.save()

                pm_teams_count += 1
                break

    return "Распределение успешно"


def get_teams(start_date=datetime.now()):
    """Возвращает данные по командам у которых
    дата начала проекта позднее указанной start_date."""

    team_projects = TeamProject.objects.filter(date_start__gte=start_date)
    if not team_projects.exists():
        return []

    teams = []
    for team_project in team_projects:
        if not team_project.timeslots.all().exists():
            continue

        pm_timeslot = team_project.timeslots.filter(
            participant__role=Participant.PRODUCT_MANAGER
        )
        if not pm_timeslot.exists():
            continue

        students_timeslots = team_project.timeslots.filter(
            participant__role=Participant.STUDENT,
        )
        teams.append(
            {
                "pm_timeslot": pm_timeslot,
                "pm": pm_timeslot[0].participant,
                "students_timeslots": students_timeslots,
                "students": Participant.objects.filter(
                    role=Participant.STUDENT, timeslots__in=students_timeslots
                ),
            }
        )

    return teams


def cancel_distribution(start_date=datetime.now()):
    """Отмена распределения, для проектов у которых дата начала позднее
    указанной start_date."""

    busy_timeslots = TimeSlot.objects.filter(
        team_project__date_start__gte=start_date,
    )
    if not busy_timeslots.exists():
        return "Не найдено временных слотов!"

    projects_to_delete = TeamProject.objects.filter(timeslots__in=busy_timeslots)
    projects_to_delete.delete()

    return "Отмена распределения выполнена успешно"


def get_unallocated_students():
    """Выборка нераспределенных по ПМам и группам учеников."""

    students = Participant.objects.filter(role=Participant.STUDENT)
    unallocated_students = []
    for student in students:
        # исключая прошедшие проекты
        actual_student_timeslots = student.timeslots.exclude(
            team_project__date_end__lte=datetime.now()
        ).values("team_project")

        if all(item["team_project"] is None for item in actual_student_timeslots):
            unallocated_students.append(student)

    return unallocated_students


def get_unallocated_students_optimized():
    slots_with_actual_project = TimeSlot.objects.filter(
        team_project__isnull=False,
        team_project__date_start__gte=datetime.now(),
    )

    return (
        Participant.objects.filter(
            role=Participant.STUDENT,
        )
        .exclude(
            timeslots__in=slots_with_actual_project,
        )
        .distinct()
    )


def make_timeslots(time_start, time_end, tg_id, project=None):
    """Создание таймслотов для ученика или менеджера."""

    participant = Participant.objects.get(tg_id=tg_id)
    time_stamps = _timestamps_by_range(time_start, time_end)
    for time_stamp in time_stamps:
        _create_timeslot(
            time_slot=time_stamp,
            participant=participant,
            team_project=project,
        )


def _timestamps_by_range(time_start, time_end):
    time_delta = timedelta(minutes=CALL_TIME_MINUTES)
    timestamps = []

    while time_start <= time_end:
        timestamps.append(time_start.time())
        time_start += time_delta

    return timestamps


def _create_timeslot(time_slot=None, participant=None, team_project=None):
    """Создает записи таймслота для заданого времени, проекта и участника."""
    return TimeSlot.objects.get_or_create(
        time_slot=time_slot,
        participant=participant,
        team_project=team_project,
    )
