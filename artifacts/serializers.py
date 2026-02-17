from rest_framework import serializers

from artifacts.models import CollectibleItem


class CollectibleItemSerializer(serializers.ModelSerializer):
    """Сериализатор для модели CollectibleItem.
    Преобразует данные модели CollectibleItem в формат JSON и обратно.
    Используется для валидации и сериализации данных при создании и передаче
    информации о коллекционных предметах через API. Включает валидацию
    географических координат (широты и долготы) на соответствие допустимым диапазонам.
    """

    class Meta:
        """Метакласс сериализатора, определяющий модель и поля для сериализации.
        Атрибуты:
            model (Model): Модель Django, с которой работает сериализатор.
            fields (tuple): Кортеж полей модели, которые будут включены в сериализацию.
        """

        model = CollectibleItem
        fields = ("name", "uid", "value", "latitude", "longitude", "picture")

    def validate_latitude(self, value: float) -> float:
        """Валидирует значение широты.
        Проверяет, что переданное значение находится в допустимом диапазоне:
        от -90.0 до 90.0 градусов."""

        if not -90.0 <= value <= 90.0:
            raise serializers.ValidationError(
                "Широта должна быть в диапазоне от -90 до 90."
            )
        return value

    def validate_longitude(self, value: float) -> float:
        """Валидирует значение долготы.
        Проверяет, что переданное значение находится в допустимом диапазоне:
        от -180.0 до 180.0 градусов."""

        if not -180.0 <= value <= 180.0:
            raise serializers.ValidationError(
                "Долгота должна быть в диапазоне от -180 до 180."
            )
        return value
