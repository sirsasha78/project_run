from django.db import models
from django.contrib.auth.models import User


class Run(models.Model):
    """Модель для хранения информации о забеге атлета.
    Представляет собой запись о тренировочном или соревновательном забеге,
    связанную с конкретным пользователем (атлетом). Содержит дату и время начала
    забега, ссылку на пользователя и комментарий."""

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
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий",
        help_text="Дополнительная информация о забеге: состояние, погода, настроение и т.д.",
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
