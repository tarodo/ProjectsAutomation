from django.db import models


class CommonParticipant(models.Model):
    """Абстрактный участник проекта."""

    tg_id = models.PositiveIntegerField(
        verbose_name="Telegram id",
        blank=False,
        null=False,
    )
    tg_username = models.CharField(
        verbose_name="Ник в Telegram",
        max_length=32,
        blank=True,
        null=True,
    )
    name = models.CharField(
        verbose_name="Имя",
        max_length=32,
        blank=False,
        null=False,
    )
    surname = models.CharField(
        verbose_name="Фамилия",
        max_length=32,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.name} {self.surname}"

    class Meta:
        abstract = True


class ProductManager(CommonParticipant):
    """Продакт-менеджер."""

    students = models.ManyToManyField(
        to="Student",
        through="TimeSlot",
    )

    def __str__(self):
        return super().__str__()

    class Meta:
        verbose_name = "Продакт-менеджер"
        verbose_name_plural = "Продакт-менеджеры"


class Student(CommonParticipant):
    """Ученик курсов."""

    BEGINNER = "BG"
    BEGINNER_PLUS = "BG+"
    JUNIOR = "JR"
    STUDENT_LEVEL_CHOICES = [
        (BEGINNER, "Новичок"),
        (BEGINNER_PLUS, "Новичок+"),
        (JUNIOR, "Джуниор"),
    ]

    level = models.CharField(
        verbose_name="Уровень ученика",
        blank=False,
        null=False,
        max_length=3,
        choices=STUDENT_LEVEL_CHOICES,
        default=BEGINNER,
    )

    def __str__(self):
        return super().__str__()

    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"


class TimeSlot(models.Model):
    """Слот времени. Связывает ученика и продакт-менеджера.
    Все поля кроме time_slot могут быть null=True,
    т.е. на это время может вообще не быть созвона ни у кого."""

    time_slot = models.TimeField(
        verbose_name="Время начала созвона", blank=False, null=False
    )
    # TODO: м.б. все-таки продакт обязателен,
    # если на его расписании все завязано?
    product_manager = models.ForeignKey(
        verbose_name="Продакт-менеджер",
        to=ProductManager,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    student = models.ForeignKey(
        verbose_name="Ученик",
        to="Student",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    project_team = models.ForeignKey(
        verbose_name="Проект команды",
        to="TeamProject",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"{self.time_slot} / {self.product_manager} - {self.student}"

    class Meta:
        verbose_name = "Слот времени"
        verbose_name_plural = "Слоты времени"

        # TODO: добавить ограничения
        constraints = [
            models.UniqueConstraint(
                fields=["time_slot", "product_manager", "student", "project_team"],
                name="Менеджер, студент, проект и слот времени",
            ),
            models.UniqueConstraint(
                fields=["product_manager", "student", "project_team"],
                name="Менеджер, студент и проект",
            ),
            models.UniqueConstraint(
                fields=["time_slot", "student", "project_team"],
                name="Слот времени, студент и проект",
            ),
            models.UniqueConstraint(
                fields=["student", "project_team"],
                name="Студент и проект команды",
            ),
        ]


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
    """Конкретный проект команды с необходимой организационной информацией."""

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
        return f"{self.id} / {self.date_start.date()} - {self.project.name}"

    class Meta:
        verbose_name = "Проект команды"
        verbose_name_plural = "Проекты команд"
