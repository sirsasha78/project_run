from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.conf import settings
from geopy.distance import geodesic


from app_run.models import Run, AthleteInfo, Challenge, Position
from app_run.serializers import (
    RunSerializer,
    UserSerializer,
    AthleteInfoSerializer,
    ChallengeSerializer,
    PositionSerializer,
    UserDetailSerializer,
)
from app_run.paginations import CustomPagination
from app_run.utils import calculate_run_distance, check_and_collect_artifacts
from app_run.challenge_service import (
    create_challenge_ten_runs,
    create_challenge_50_kilometers,
)
from artifacts.models import CollectibleItem


@api_view(["GET"])
def company_details(request: Request) -> Response:
    """Возвращает основные данные о компании.
    Предоставляет информацию о названии компании, слогане и контактных данных.
    Данные берутся из настроек приложения (settings).
    Args:
        request (Request): Объект HTTP-запроса. Используется для обработки входящего GET-запроса.
    Returns:
        Response: JSON-ответ с данными о компании и статусом 200 OK."""

    data = {
        "company_name": settings.COMPANY_NAME,
        "slogan": settings.SLOGAN,
        "contacts": settings.CONTACTS,
    }
    return Response(data, status=status.HTTP_200_OK)


class RunViewSet(viewsets.ModelViewSet):
    """Набор представлений для модели Run, обеспечивающий стандартные действия CRUD (создание, чтение, обновление, удаление).
    Этот ViewSet предоставляет полный набор операций для управления объектами модели Run
    через REST API, включая получение списка объектов, просмотр отдельного объекта,
    создание новых объектов, частичное и полное обновление, а также удаление.
    Атрибуты:
        queryset (django.db.models.QuerySet): Набор записей модели Run с предзагрузкой
            связанного объекта athlete. Используется для оптимизации запросов к базе данных
            путём уменьшения количества обращений при сериализации.
        serializer_class (Serializer): Класс сериализатора, используемый для преобразования
            объектов модели Run в формат JSON и обратно. Определяет поля, которые будут
            включены в API-ответы и как данные будут валидироваться при создании/обновлении.
        pagination_class (Pagination): Класс пагинации CustomPagination, обеспечивающий
                                       постраничный вывод результатов.
        filter_backends (list): Список бэкендов фильтрации, используемых для обработки
            параметров фильтрации и сортировки в запросах.
        filterset_fields (list): Поля модели, по которым доступна точная фильтрация
            через параметры URL (например, ?status=completed&athlete=1).
        ordering_fields (list): Поля, по которым разрешена сортировка результатов
            через параметр ordering (например, ?ordering=created_at).
    """

    queryset = Run.objects.all().select_related("athlete")
    serializer_class = RunSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "athlete"]
    ordering_fields = ["created_at"]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Набор представлений для чтения данных пользователей с возможностью фильтрации по типу.
    Предоставляет эндпоинты для получения списка пользователей и детальной информации о пользователе.
    Исключает суперпользователей из выборки по умолчанию.
    Атрибуты:
        queryset (QuerySet): Базовый набор объектов User, исключающий суперпользователей.
        serializer_class (Serializer): Сериализатор, используемый для преобразования объектов User в JSON.
        pagination_class (Pagination): Класс пагинации CustomPagination, обеспечивающий
                                       постраничный вывод результатов.
        filter_backends (list): Список классов фильтрации, применяемых к набору запросов.
            В данном случае используется поиск по полям имени и фамилии.
        search_fields (list): Поля модели User, по которым осуществляется поиск при наличии параметра `search` в запросе.
        ordering_fields (list): Поля модели User, по которым разрешена сортировка
                                через параметр `ordering` в URL. Доступна сортировка по дате регистрации.
    """

    queryset = User.objects.all().exclude(is_superuser=True)
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["first_name", "last_name"]
    ordering_fields = ["date_joined"]

    def get_serializer_class(self) -> UserSerializer | UserDetailSerializer:
        """Определяет и возвращает класс сериализатора в зависимости от выполняемого действия.
        Используется для разделения логики сериализации при получении списка пользователей
        и детальной информации о пользователе.
        Возвращаемые значения:
            UserSerializer: Если действие — 'list' (получение списка).
            UserDetailSerializer: Если действие — 'retrieve' (получение одного объекта).
            Родительский класс сериализатора: Для любых других действий."""

        if self.action == "list":
            return UserSerializer
        if self.action == "retrieve":
            return UserDetailSerializer
        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet[User]:
        """Возвращает отфильтрованный набор пользователей в зависимости от параметра 'type' в GET-запросе.
        Если параметр 'type' присутствует и равен 'coach', возвращаются только пользователи с is_staff=True.
        Если параметр 'type' равен 'athlete', возвращаются пользователи с is_staff=False.
        Если параметр отсутствует или имеет другое значение, возвращается базовый queryset (без суперпользователей).
        Returns:
            QuerySet[User]: Отфильтрованный набор экземпляров модели User."""

        users = self.queryset
        users_type = self.request.query_params.get("type", None)
        if users_type == "coach":
            return users.filter(is_staff=True)
        elif users_type == "athlete":
            return users.filter(is_staff=False)
        return users


class StartView(APIView):
    """Представление для старта забега.
    Позволяет изменить статус забега с 'инициализирован' на 'в процессе',
    если забег существует и его текущий статус позволяет начать."""

    def post(self, request: Request, *args, **kwargs) -> Response:
        """Обрабатывает POST-запрос на старт забега.
        Пытается найти забег по переданному в URL идентификатору (run_id).
        Если забег не найден, возвращает ошибку 404.
        Если статус забега — 'инициализирован' (INIT), изменяет его на 'в процессе' (IN_PROGRESS)
        и сохраняет. В случае успеха возвращает сообщение об успешном старте.
        Если забег уже начат или завершён, возвращает ошибку 400."""

        try:
            run = Run.objects.get(id=kwargs["run_id"])
        except Run.DoesNotExist:
            return Response(
                {"message": "Забег не существует"}, status=status.HTTP_404_NOT_FOUND
            )
        if run.status == Run.RUN_STATUS_INIT:
            run.status = Run.RUN_STATUS_IN_PROGRESS
            run.save()
            return Response({"status": "Забег начат"}, status=status.HTTP_200_OK)
        return Response(
            {"message": "Забег уже начат или закончен"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class FinishView(APIView):
    """Представление для завершения забега.
    Позволяет изменить статус забега с "в процессе" на "завершён".
    Доступно по POST-запросу. Проверяет существование забега и его текущий статус."""

    def post(self, request: Request, *args, **kwargs) -> Response:
        """Обрабатывает POST-запрос на завершение забега.
        Пытается найти забег по идентификатору, переданному в URL (`run_id`).
        Если забег не найден, возвращает HTTP 404.
        Если забег уже завершён или не находится в статусе «в процессе», возвращает HTTP 400.
        Если забег активен, изменяет его статус на «завершён», сохраняет объект,
        вычисляет пройденную дистанцию на основе собранных GPS-позиций и сохраняет её.
        Дополнительно проверяет, является ли этот забег 10-м завершённым для пользователя.
        В случае выполнения условия — создаёт новое испытание (Challenge)."""

        try:
            run = Run.objects.get(id=kwargs["run_id"])
        except Run.DoesNotExist:
            return Response(
                {"message": "Забег не существует"}, status=status.HTTP_404_NOT_FOUND
            )

        if run.status == Run.RUN_STATUS_IN_PROGRESS:
            run.status = Run.RUN_STATUS_FINISHED
            run.save()

            all_positions = list(run.positions.all())
            run.distance = calculate_run_distance(all_positions)
            run.save()

            finished_run = Run.objects.filter(
                athlete=run.athlete, status=Run.RUN_STATUS_FINISHED
            )

            create_challenge_ten_runs(run.athlete, finished_run)
            create_challenge_50_kilometers(run.athlete, finished_run)

            return Response({"status": "Забег закончен"}, status=status.HTTP_200_OK)
        return Response(
            {"message": "Забег не запущен или закончен"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class AthleteInfoView(APIView):
    """Представление для управления информацией об атлете.
    Позволяет получать и обновлять данные о пользователе-атлете, такие как цели и вес.
    Использует сериализатор AthleteInfoSerializer для валидации и сериализации данных.
    Доступ к данным осуществляется по идентификатору пользователя (user_id).
    Атрибуты:
        serializer_class (type): Класс сериализатора, используемый для преобразования
                                 данных модели AthleteInfo в JSON и обратно."""

    serializer_class = AthleteInfoSerializer

    def get_object(self, user_id: int) -> User | None:
        """Получает объект пользователя по его идентификатору.
        Метод пытается найти пользователя в базе данных по заданному ID.
        Если пользователь не найден, возвращает None."""

        try:
            user = User.objects.get(id=user_id)
            return user
        except User.DoesNotExist:
            return None

    def get(self, request: Request, *args, **kwargs) -> Response:
        """Обрабатывает GET-запрос для получения информации об атлете.
        Находит пользователя по user_id из URL. Если пользователь существует,
        возвращает или создаёт объект AthleteInfo и сериализует его данные.
        В противном случае возвращает ошибку 404."""

        user = self.get_object(kwargs["user_id"])
        if not user:
            return Response(
                {"message": "Пользователь не существует"},
                status=status.HTTP_404_NOT_FOUND,
            )

        athleteinfo, _ = AthleteInfo.objects.select_related("athlete").get_or_create(
            athlete=user
        )
        serializer = self.serializer_class(athleteinfo)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, *args, **kwargs) -> Response:
        """Обрабатывает PUT-запрос для обновления информации об атлете.
        Находит пользователя по user_id. Если пользователь не существует,
        возвращает ошибку 404. Обновляет или создаёт объект AthleteInfo.
        В случае ошибки валидации возвращает соответствующее сообщение."""

        user = self.get_object(kwargs["user_id"])
        if not user:
            return Response(
                {"message": "Пользователь не существует"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            athleteinfo, _ = AthleteInfo.objects.select_related(
                "athlete"
            ).update_or_create(
                athlete=user,
                defaults={"goals": data["goals"], "weight": data["weight"]},
            )
            serializer = self.serializer_class(athleteinfo)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    """Набор представлений для работы с объектами Challenge (вызовы/испытания).
    Предоставляет только чтение (список и детали) объектов модели Challenge.
    Поддерживает фильтрацию по полю `athlete`, что позволяет получать все вызовы,
    связанные с конкретным спортсменом.
    Атрибуты:
        queryset (QuerySet): Набор данных, содержащий все объекты модели Challenge.
        serializer_class (ChallengeSerializer): Сериализатор, используемый для преобразования
            объектов Challenge в JSON и обратно.
        filter_backends (list): Список бэкендов фильтрации. Используется DjangoFilterBackend
            для поддержки фильтрации через параметры запроса.
        filterset_fields (list): Поля модели, по которым доступна фильтрация.
            В данном случае — только поле `athlete`."""

    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["athlete"]


class PositionViewSet(viewsets.ModelViewSet):
    """Набор представлений для модели Position.
    Предоставляет полный набор операций CRUD (создание, чтение, обновление, удаление)
    для объектов модели Position через API. Поддерживает фильтрацию по полям,
    указанным в `filterset_fields`.
    Атрибуты:
        queryset (QuerySet): Набор данных, содержащий все объекты модели Position.
        serializer_class (Serializer): Класс сериализатора, используемый для преобразования
            объектов модели в JSON и обратно.
        filter_backends (list): Список бэкендов фильтрации, используемых для фильтрации запросов.
            В данном случае используется DjangoFilterBackend для поддержки фильтрации
            на основе параметров запроса.
        filterset_fields (list): Список полей модели, по которым разрешена фильтрация.
            Пользователь может фильтровать объекты по полю `run`."""

    queryset = Position.objects.all().select_related("run__athlete")
    serializer_class = PositionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["run"]

    def perform_create(self, serializer: PositionSerializer) -> None:
        """Выполняет дополнительные действия при создании новой позиции.
        Извлекает данные из валидированного сериализатора, определяет пользователя
        (участника забега) и координаты. Проверяет, находятся ли в указанной точке
        какие-либо артефакты, и при наличии — зачисляет их пользователю.
        После выполнения бизнес-логики сохраняет объект Position в базу данных.
        Примечание:
            Метод вызывается автоматически при успешной валидации данных
            в процессе создания объекта через API."""

        data = serializer.validated_data
        user = data["run"].athlete
        latitude = data["latitude"]
        longitude = data["longitude"]
        check_and_collect_artifacts(user, latitude, longitude)
        serializer.save()
