from itertools import groupby, product
from operator import itemgetter

from bot.models import ProductManager, Student, TimeSlot


def make_teams():
    """
    Вычислить кол-во команд на 1 Пма,
    пройтись по временам каждого ПМа и фильтровать учеников на это время, по первому попавшемуся,
    если набралось 3 - сохранить в этот таймслот, если нет - подбор на следующее время,
    если максимум команд - переход к другому ПМу,
    начинать с тех у кого мало таймслотов (и ПМы и ученики)

    for pm in ProductManagers.all(timeslots_sort=asc):
        pm_teams_count = 0
        pm_timeslots = pm_timeslots.filter(status_isnot='used').groupby(count(timeslots), product_id)
        for pm_timeslot in pm_timeslots
            if pm_teams_count = N
                break
            for level in LEVELS:
                studs = Student.filter(timeslot=pm_timeslot.timeslot, level=level, status_isnot='approved').groupby(count(timeslot))
                if studs.count() < 3
                    continue
                team = studs[:3]
                for s in team:
                    s.update(manager=pm_timeslot.manager, status='approved')
                pm_timeslot.status = 'used'
                pm_team_count += 1
                break


    """

    MAX_TEAM_MEMBERS = 3
    MAX_MANAGER_TEAMS = (
        Student.objects.count() // MAX_TEAM_MEMBERS // ProductManager.objects.count()
    )

    for pm in ProductManager.all():
        pm_teams_count = 0
        pm_timeslots = TimeSlot.objects.filter(
            product_manager__isnull=False, student__isnull=True, status=TimeSlot.FREE
        )
        for pm_timeslot in pm_timeslots:
            if pm_teams_count == MAX_MANAGER_TEAMS:
                break
            for level in (Student.BEGINNER, Student.BEGINNER_PLUS, Student.JUNIOR):
                students_slots = TimeSlot.objects.filter(
                    product_manager__isnull=True,
                    student__isnull=False,
                    student__level=level,
                    time_slot=pm_timeslot.time_slot,
                    status=TimeSlot.FREE,
                )
                if students_slots.count() < MAX_TEAM_MEMBERS:
                    continue
                team = studs[:3]
                for s in team:
                    s.update(manager=pm_timeslot.manager, status="approved")
                pm_timeslot.status = "used"
                pm_team_count += 1
                break

    managers_slots = TimeSlot.objects.filter(
        product_manager__isnull=False, student__isnull=True
    )
    students_slots = TimeSlot.objects.filter(
        product_manager__isnull=True, student__isnull=False
    )
    for manager_slot in managers_slots:
        current_manager_time_slot = manager_slot.time_slot
        students_slots.filter(time_slot=current_manager_time_slot)

    managers_slots_list = list(
        managers_slots.values("id", "time_slot", "product_manager_id")
    )
    students_slots_list = list(
        students_slots.values("id", "time_slot", "student_id", "student__level")
    )

    managers_slots_list = sorted(
        managers_slots_list, key=itemgetter("product_manager_id", "time_slot")
    )
    students_slots_list = sorted(
        students_slots_list, key=itemgetter("student__level", "student_id", "time_slot")
    )

    for k, v in groupby(
        managers_slots_list,
        key=itemgetter(
            "product_manager_id",
            "time_slot",
        ),
    ):
        print(k)
        print(list(v))
        print()

    print()

    for k, v in groupby(
        students_slots_list,
        key=itemgetter(
            "student__level",
            "student_id",
            "time_slot",
        ),
    ):
        print(k)
        print(list(v))
        print()
