from rest_framework import serializers

from app_run.models import Run


class RunSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Run.
    Преобразует объекты модели Run в формат JSON и обратно, обеспечивая
    сериализацию всех полей модели. Используется для передачи данных о забегах
    через API.
    Атрибуты:
        model (Model): Модель Django, с которой работает сериализатор — Run.
        fields (str): Определяет, что все поля модели должны быть включены в сериализацию.
    """

    class Meta:
        """Настройка сериализатора: использует модель Run и включает все поля."""

        model = Run
        fields = ("created_at", "athlete", "comment")
