from django.db import models


class CollectibleItem(models.Model):
    """Модель, представляющая коллекционный артефакт в системе.
    Хранит информацию о находке, включая её название, уникальный идентификатор,
    географические координаты, ссылку на изображение и числовую ценность.
    Используется для отображения и управления артефактами в приложении."""

    name = models.CharField(
        max_length=255,
        verbose_name="Артефакт",
        help_text="Название артефакта, отображаемое в интерфейсе.",
    )
    uid = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Идентификатор",
        help_text="Уникальный строковый идентификатор артефакта.",
    )
    latitude = models.FloatField(
        verbose_name="Широта", help_text="Географическая широта: от -90 до 90 градусов."
    )
    longitude = models.FloatField(
        verbose_name="Долгота",
        help_text="Географическая долгота: от -180 до 180 градусов.",
    )
    picture = models.URLField(
        verbose_name="Изображение", help_text="Прямая ссылка на изображение артефакта."
    )
    value = models.IntegerField(
        blank=True,
        null=True,
        default=None,
        verbose_name="Значение",
        help_text="Числовая ценность артефакта, например, в игровых очках.",
    )

    class Meta:
        """Метаданные модели."""

        verbose_name = "Артефакт"
        verbose_name_plural = "Артефакты"
        indexes = [
            models.Index(fields=["latitude", "longitude"]),
        ]

    def __str__(self) -> str:
        """Возвращает строковое представление объекта артефакта."""

    def __str__(self) -> str:
        """Возвращает строковое представление артефакта."""

        return self.name
