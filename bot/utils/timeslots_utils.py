from bot.models import ProductManager, Student, TimeSlot


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
