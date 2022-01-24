from django.db import models


class Participant(models.Model):
    """Участник проекта."""

    tg_id = models.PositiveIntegerField(
        verbose_name="Telegram id",
        unique=True,
        blank=True,
        null=True,
    )
    tg_username = models.CharField(
        verbose_name="Ник в Telegram",
        max_length=32,
        blank=False,
        null=False,
    )
    discord_username = models.CharField(
        verbose_name="discord username",
        max_length=32,
        blank=True,
        null=True,
    )
    name = models.CharField(
        verbose_name="Имя и фамилия",
        max_length=32,
        blank=False,
        null=False,
    )
    STUDENT = "ST"
    PRODUCT_MANAGER = "PM"
    PARTICIPANT_ROLES_CHOICES = (
        (STUDENT, "Ученик"),
        (PRODUCT_MANAGER, "PM"),
    )
    role = models.CharField(
        verbose_name="Роль",
        max_length=3,
        choices=PARTICIPANT_ROLES_CHOICES,
        default=STUDENT,
    )

    BEGINNER = "BG"
    BEGINNER_PLUS = "BG+"
    JUNIOR = "JR"
    NOT_AVAIBLE = "N/A"
    STUDENT_LEVEL_CHOICES = [
        (BEGINNER, "Новичок"),
        (BEGINNER_PLUS, "Новичок+"),
        (JUNIOR, "Джуниор"),
        (NOT_AVAIBLE, "Не применимо"),
    ]
    level = models.CharField(
        verbose_name="Уровень ученика",
        blank=False,
        null=False,
        max_length=3,
        choices=STUDENT_LEVEL_CHOICES,
        default=NOT_AVAIBLE,
    )

    is_far_east = models.BooleanField(
        verbose_name="Из ДВ?",
        default=False,
        blank=True,
        null=True,
    )

    def __str__(self):
        levels = dict(self.STUDENT_LEVEL_CHOICES)
        roles = dict(self.PARTICIPANT_ROLES_CHOICES)
        if self.level:
            lvl = levels[self.level]
        return f"{roles[self.role]}: {self.name} ({self.tg_username})"

    class Meta:
        verbose_name = "Участник проекта"
        verbose_name_plural = "Участник проекта"


class TimeSlot(models.Model):
    """Слот времени. Время, участник и проект уникальны."""

    time_slot = models.TimeField(
        verbose_name="Время начала созвона",
        blank=False,
        null=False,
    )
    participant = models.ForeignKey(
        verbose_name="Участник",
        related_name="timeslots",
        to="Participant",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    team_project = models.ForeignKey(
        verbose_name="Проект команды",
        related_name="timeslots",
        to="TeamProject",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return (
            f"{self.time_slot.strftime('%H:%M')}"
            f" / {self.participant}"
            f" / {self.team_project}"
        )

    class Meta:
        verbose_name = "Слот времени"
        verbose_name_plural = "Слоты времени"
        # TODO: добавить ограничения


class Project(models.Model):
    """Типовой проект с кратким описанием и ссылкой на бриф."""

    name = models.CharField(
        verbose_name="Название проекта",
        max_length=256,
        blank=False,
        null=False,
    )
    description = models.TextField(
        verbose_name="Краткое описание",
        blank=True,
        null=True,
    )
    link_doc = models.URLField(
        verbose_name="Ссылка на бриф",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Типовой проект"
        verbose_name_plural = "Типовой проект"


class TeamProject(models.Model):
    """Конкретный проект конкретной команды
    с необходимой организационной информацией."""

    date_start = models.DateTimeField(
        verbose_name="Дата и время начала проекта",
        blank=False,
        null=False,
    )
    date_end = models.DateTimeField(
        verbose_name="Дата и время окончания проекта",
        blank=False,
        null=False,
    )
    project = models.ForeignKey(
        verbose_name="Описание проекта",
        related_name="teamprojects",
        to="Project",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    discord_server_link = models.URLField(
        verbose_name="Ссылка на discord сервер",
        blank=True,
        null=True,
    )
    trello_desk_link = models.URLField(
        verbose_name="Ссылка на trello доску",
        blank=True,
        null=True,
    )

    def __str__(self):
        return (
            f"id{self.id} / {self.project.name} / "
            f"{self.date_start.strftime('%d.%m.%Y')}"
            f" - {self.date_end.strftime('%d.%m.%Y')}"
        )

    class Meta:
        verbose_name = "Проект команды"
        verbose_name_plural = "Проекты команд"
