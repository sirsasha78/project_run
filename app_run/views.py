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

from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializer
from app_run.paginations import CustomPagination


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
        Пытается найти забег по переданному в URL идентификатору (`run_id`).
        Если забег не найден, возвращает статус 404.
        Если забег уже завершён или не запущен, возвращает статус 400.
        Если забег активен, изменяет его статус на "завершён" и сохраняет."""

        try:
            run = Run.objects.get(id=kwargs["run_id"])
        except Run.DoesNotExist:
            return Response(
                {"message": "Забег не существует"}, status=status.HTTP_404_NOT_FOUND
            )
        if run.status == Run.RUN_STATUS_IN_PROGRESS:
            run.status = Run.RUN_STATUS_FINISHED
            run.save()
            return Response({"status": "Забег закончен"}, status=status.HTTP_200_OK)
        return Response(
            {"message": "Забег не запущен или закончен"},
            status=status.HTTP_400_BAD_REQUEST,
        )
