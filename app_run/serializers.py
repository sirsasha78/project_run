from rest_framework import serializers
from django.contrib.auth.models import User

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
        fields = ("id", "created_at", "athlete", "comment")


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User.
    Преобразует объекты модели User в формат JSON и обратно.
    Включает стандартные поля пользователя, а также вычисляемое поле `type`,
    которое определяет тип пользователя на основе его прав доступа:
    - 'coach' — если пользователь имеет статус персонала (is_staff=True),
    - 'athlete' — для всех остальных пользователей.
    Используется в API для предоставления информации о пользователях
    с различением по ролям без необходимости передачи служебных полей напрямую."""

    type = serializers.SerializerMethodField()

    class Meta:
        """Метакласс сериализатора, определяющий модель и поля для сериализации.
        Атрибуты:
            model (User): Модель, на основе которой строится сериализатор.
            fields (tuple): Кортеж полей модели, включаемых в сериализацию,
                           включая вычисляемое поле `type`."""

        model = User
        fields = ("id", "date_joined", "username", "last_name", "first_name", "type")

    def get_type(self, obj: User) -> str:
        """Возвращает тип пользователя на основе его статуса персонала.
        Метод используется для заполнения поля `type` в сериализованных данных.
        Определяет роль пользователя: тренер (coach) или спортсмен (athlete).
        Аргументы:
            obj (User): Экземпляр модели User, для которого определяется тип."""

        return "coach" if obj.is_staff else "athlete"
