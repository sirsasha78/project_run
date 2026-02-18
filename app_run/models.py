from django.db import models
from django.contrib.auth.models import User


class Run(models.Model):
    """Модель для хранения информации о забеге атлета.
    Представляет собой запись о тренировочном или соревновательном забеге,
    связанную с конкретным пользователем (атлетом). Содержит дату и время начала
    забега, ссылку на пользователя, статус забега и комментарий."""

    RUN_STATUS_INIT = "init"
    RUN_STATUS_IN_PROGRESS = "in_progress"
    RUN_STATUS_FINISHED = "finished"

    STATUS_CHOICES = (
        ("init", "Забег инициализирован"),
        ("in_progress", "Забег начат"),
        ("finished", "Забег закончен"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата начала забега",
        help_text="Автоматически устанавливается при создании записи.",
    )
    athlete = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Атлет",
        help_text="Пользователь, который совершил забег.",
        related_name="runs",
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий",
        help_text="Дополнительная информация о забеге: состояние, погода, настроение и т.д.",
    )
    status = models.CharField(
        max_length=11,
        choices=STATUS_CHOICES,
        db_index=True,
        default=RUN_STATUS_INIT,
        verbose_name="Статус забега",
        help_text="Текущий статус забега: инициализация, в процессе, завершён.",
    )
    distance = models.FloatField(
        blank=True,
        default=0.0,
        verbose_name="Дистанция",
        help_text="Расстояние, которое пробежал атлет",
    )

    class Meta:
        """Метакласс модели Run.
        Определяет поведение модели на уровне базы данных и интерфейса администратора.
        """

        verbose_name = "Забег"
        verbose_name_plural = "Забеги"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Возвращает строковое представление объекта забега."""

        return f"Забег - {self.created_at} - {self.athlete.username}"


class AthleteInfo(models.Model):
    """Модель для хранения информации о спортсмене.
    Содержит данные о целях, весе и пользователе-спортсмене. Каждый пользователь
    может иметь только одну запись с информацией о себе как об атлете."""

    goals = models.CharField(
        max_length=255,
        verbose_name="Цели",
        blank=True,
        null=True,
        default=None,
        help_text="Описание целей спортсмена.",
    )
    weight = models.IntegerField(
        blank=True,
        null=True,
        default=None,
        verbose_name="Вес",
        help_text="Текущий вес спортсмена в килограммах.",
    )
    athlete = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="athlete_info",
        verbose_name="Атлет",
        help_text="Связанный пользователь, представляющий атлета.",
    )

    class Meta:
        """Метакласс модели AthleteInfo."""

        verbose_name = "Информация о спортсмене"
        verbose_name_plural = "Информация о спортсменах"

    def __str__(self) -> str:
        """Возвращает строковое представление объекта AthleteInfo."""

        return f"Информация о спортсмене - {self.athlete.username}"


class Challenge(models.Model):
    """Модель для представления испытания, связанного с атлетом.
    Испытание создаётся для конкретного пользователя (атлета) и содержит информацию
    о названии испытания. Связь с пользователем осуществляется через внешний ключ.
    Поддерживает строковое представление и настройки отображения в административной панели.
    """

    full_name = models.CharField(
        max_length=255,
        verbose_name="Испытание",
        help_text="Введите полное название испытания.",
    )
    athlete = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="challenges",
        verbose_name="Атлет",
        help_text="Выберите пользователя, который проходит это испытание.",
    )

    class Meta:
        """Метакласс модели для настройки отображения в админке."""

        verbose_name = "Испытание"
        verbose_name_plural = "Испытания"

    def __str__(self) -> str:
        """Возвращает строковое представление объекта испытания."""

        return f"Испытание атлета {self.athlete.username}"


class Position(models.Model):
    """Модель для хранения географических координат участника во время забега.
    Каждый объект модели представляет собой одну точку местоположения (широту и долготу),
    зафиксированную в определённый момент времени в рамках конкретного забега.
    Привязывается к участнику через связь с моделью Run."""

    run = models.ForeignKey(
        Run, on_delete=models.CASCADE, related_name="positions", verbose_name="Забег"
    )
    latitude = models.FloatField(
        verbose_name="Широта", help_text="Географическая широта: от -90 до 90 градусов."
    )
    longitude = models.FloatField(
        verbose_name="Долгота",
        help_text="Географическая долгота: от -180 до 180 градусов.",
    )
    date_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Время фиксации",
        help_text="Точная временная метка позиции, переданная трекером.",
    )

    class Meta:
        """Метаданные модели Position."""

        verbose_name = "Позиция"
        verbose_name_plural = "Позиции"

    def __str__(self) -> str:
        """Возвращает строковое представление объекта Position."""

        return f"Координаты - {self.run.athlete.username}"
