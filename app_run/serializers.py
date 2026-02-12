from rest_framework import serializers
from django.contrib.auth.models import User

from app_run.models import Run, AthleteInfo, Challenge


class AthleteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User, предназначенный для представления данных спортсмена.
    Используется для сериализации и десериализации данных пользователей,
    когда они выступают в роли спортсменов. Включает основные поля профиля:
    идентификатор, имя пользователя, фамилию и имя.
    Атрибуты:
        Meta (класс): Вложенный класс, определяющий модель и поля сериализатора."""

    class Meta:
        """Метакласс сериализатора, определяющий связь с моделью и поля для сериализации.
        Атрибуты:
            model (django.db.models.Model): Модель, с которой работает сериализатор.
            fields (tuple): Кортеж полей модели, которые будут включены в сериализацию.
        """

        model = User
        fields = ("id", "username", "last_name", "first_name")


class RunSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Run.
    Преобразует объекты модели Run в формат JSON и обратно, обеспечивая
    сериализацию указанных полей модели. Используется для передачи данных о забегах
    через API. Включает вложенные данные спортсмена с помощью AthleteSerializer.
    Атрибуты:
        athlete_data (AthleteSerializer): Вложенный сериализатор для отображения
            данных спортсмена. Доступен только для чтения и автоматически
            заполняется данными связанного объекта Athlete."""

    athlete_data = AthleteSerializer(source="athlete", read_only=True)

    class Meta:
        """Метакласс сериализатора RunSerializer.
        Определяет модель Django и поля, которые будут сериализованы."""

        model = Run
        fields = ("id", "created_at", "athlete", "comment", "status", "athlete_data")


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User.
    Преобразует объекты модели User в формат JSON и обратно. Включает стандартные поля пользователя,
    а также вычисляемые поля:
    - `type` — определяет роль пользователя (тренер или спортсмен) на основе прав доступа;
    - `runs_finished` — количество завершённых забегов, связанных с пользователем.
    Используется в API для предоставления информации о пользователях
    с различением по ролям без необходимости передачи служебных полей напрямую."""

    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()

    class Meta:
        """Метакласс сериализатора, определяющий модель и поля для сериализации.
        Атрибуты:
            model (User): Модель, на основе которой строится сериализатор.
            fields (tuple): Кортеж полей модели, включаемых в сериализацию,
                           включая вычисляемое поле `type`."""

        model = User
        fields = (
            "id",
            "date_joined",
            "username",
            "last_name",
            "first_name",
            "type",
            "runs_finished",
        )

    def get_type(self, obj: User) -> str:
        """Возвращает тип пользователя на основе его статуса персонала.
        Метод используется для заполнения поля `type` в сериализованных данных.
        Определяет роль пользователя: тренер (coach) или спортсмен (athlete).
        Аргументы:
            obj (User): Экземпляр модели User, для которого определяется тип."""

        return "coach" if obj.is_staff else "athlete"

    def get_runs_finished(self, obj: User) -> int:
        """Возвращает количество завершённых забегов, связанных с пользователем.
        Подсчитывает число объектов Run, связанных с пользователем через обратную
        связь `runs`, у которых статус равен 'finished'."""

        runs = obj.runs.filter(status="finished").count()
        return runs


class AthleteInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для модели AthleteInfo.
    Преобразует данные модели AthleteInfo в формат JSON и обратно.
    Включает в себя информацию о целях, весе спортсмена и идентификаторе связанного пользователя.
    Атрибуты:
        user_id (IntegerField): Поле, содержащее идентификатор пользователя-спортсмена.
                                Получается из поля `id` связанного объекта `athlete`."""

    user_id = serializers.ReadOnlyField(source="athlete.id")

    class Meta:
        """Метакласс сериализатора, определяющий модель и поля для сериализации."""

        model = AthleteInfo
        fields = ("goals", "weight", "user_id")

    def validate_weight(self, value: int) -> int:
        """Валидатор для поля `weight`.
        Проверяет, что значение веса находится в допустимом диапазоне:
        больше 0 и меньше 900 кг."""

        if not 0 < value < 900:
            raise serializers.ValidationError(
                "Вес должен быть больше нуля и меньше 900"
            )
        return value


class ChallengeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Challenge.
    Преобразует объекты модели Challenge в формат JSON и обратно.
    Используется для сериализации данных при выполнении операций чтения и записи
    в API, связанных с испытаниями (challenges), включая информацию о полном имени
    участника и связанном спортсмене.
    """

    class Meta:
        """Метакласс сериализатора, определяющий модель и поля для сериализации."""

        model = Challenge
        fields = ("full_name", "athlete")
