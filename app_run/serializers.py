from rest_framework import serializers
from django.contrib.auth.models import User

from app_run.models import Run, AthleteInfo, Challenge, Position
from artifacts.serializers import CollectibleItemSerializer


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
        fields = (
            "id",
            "created_at",
            "athlete",
            "comment",
            "status",
            "athlete_data",
            "distance",
            "run_time_seconds",
            "speed",
        )


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
        fields = [
            "id",
            "date_joined",
            "username",
            "last_name",
            "first_name",
            "type",
            "runs_finished",
        ]

    def get_type(self, obj: User) -> str:
        """Возвращает тип пользователя на основе его статуса персонала.
        Метод используется для заполнения поля `type` в сериализованных данных.
        Определяет роль пользователя: тренер (coach) или спортсмен (athlete).
        Аргументы:
            obj (User): Экземпляр модели User, для которого определяется тип."""

        return "coach" if obj.is_staff else "athlete"

    def get_runs_finished(self, obj: User) -> int:
        """Возвращает количество завершённых забегов, связанных с пользователем.
        Метод подсчитывает число объектов модели `Run`, которые связаны с переданным
        пользователем через атрибут `count_run` и имеют статус 'finished'. Предполагается,
        что значение `count_run` уже было вычислено ранее, например, с использованием
        аннотации в queryset (например, `Count('runs', filter=Q(runs__status='finished'))`).
        """

        runs = obj.count_run
        return runs


class UserDetailSerializer(UserSerializer):
    """Сериализатор для детального представления пользователя с дополнительным полем 'items'.
    Добавляет к базовому сериализатору UserSerializer поле 'items', содержащее список
    всех объектов, связанных с пользователем через отношение 'items'. Предназначен для
    использования в API-представлениях, где требуется отобразить подробную информацию
    о пользователе, включая его связанные данные.
    Атрибуты:
        items (serializers.SerializerMethodField): Поле, возвращающее все элементы,
            связанные с пользователем. Заполняется с помощью метода get_items."""

    items = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        """Метакласс для настройки поведения сериализатора.
        Наследует метакласс из UserSerializer и расширяет список полей,
        добавляя поле 'items' к уже существующим полям базового сериализатора.
        Атрибуты:
            model (django.db.models.Model): Модель, используемая сериализатором — User.
            fields (list): Список полей модели, подлежащих сериализации, включая
                         унаследованные из UserSerializer и добавленное поле 'items'."""

        model = User
        fields = UserSerializer.Meta.fields + ["items"]

    def get_items(self, obj: User):
        """Возвращает все объекты, связанные с пользователем через отношение 'items'.
        Метод вызывается автоматически при сериализации поля 'items'.
        Получает на вход экземпляр модели User и возвращает список сериализованных
        объектов.
        """

        collected_items = list(obj.items.all())
        return CollectibleItemSerializer(collected_items, many=True).data


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


class PositionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Position.
    Предназначен для сериализации и десериализации данных о позиции участника забега,
    включая географические координаты (широту и долготу) и связь с конкретным забегом.
    Проверяет корректность координат и статус забега перед сохранением.
    Атрибуты:
        id (int): Уникальный идентификатор позиции.
        run (Run): Забег, к которому привязана позиция.
        latitude (float): Географическая широта в диапазоне от -90 до 90 градусов.
        longitude (float): Географическая долгота в диапазоне от -180 до 180 градусов.
        date_time: временная метка фиксации позиции в формате ISO 8601.
        speed (float, опционально): Скорость движения участника в момент фиксации позиции.
        distance (float, опционально): Пройденное расстояние участником к моменту фиксации позиции.
    Поле `date_time` сериализуется в формате строки с микросекундами:
    "ГГГГ-ММ-ДДTЧЧ:ММ:СС.мкс".
    """

    date_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%f")

    class Meta:
        """Метакласс сериализатора.
        Определяет модель и поля, которые будут использоваться при сериализации."""

        model = Position
        fields = (
            "id",
            "run",
            "latitude",
            "longitude",
            "date_time",
            "speed",
            "distance",
        )

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

    def validate(self, attrs: dict) -> dict:
        """Общая валидация атрибутов сериализатора.
        Проверяет, что забег, к которому привязывается позиция,
        находится в статусе 'in_progress'. Сохранение позиций разрешено только
        во время активного забега."""

        if attrs["run"].status != Run.RUN_STATUS_IN_PROGRESS:
            raise serializers.ValidationError("Забег должен быть в статусе in_progress")
        return attrs
