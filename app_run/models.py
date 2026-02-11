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
        max_length=255, verbose_name="Цели", help_text="Описание целей спортсмена."
    )
    weight = models.IntegerField(
        verbose_name="Вес", help_text="Текущий вес спортсмена в килограммах."
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
