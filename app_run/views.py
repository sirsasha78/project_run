from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from rest_framework import status
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.conf import settings

from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializer


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
        queryset (QuerySet): Набор данных, содержащий все объекты модели Run.
            Используется для получения данных из базы данных.
        serializer_class (Serializer): Класс сериализатора, используемый для преобразования
            объектов модели Run в формат JSON и обратно. Определяет поля, которые будут
            включены в API-ответы и как данные будут валидироваться при создании/обновлении.
    """

    queryset = Run.objects.all()
    serializer_class = RunSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Набор представлений для чтения данных пользователей с возможностью фильтрации по типу.
    Предоставляет эндпоинты для получения списка пользователей и детальной информации о пользователе.
    Исключает суперпользователей из выборки по умолчанию.
    Атрибуты:
        queryset (QuerySet): Базовый набор объектов User, исключающий суперпользователей.
        serializer_class (Serializer): Сериализатор, используемый для преобразования объектов User в JSON.
    """

    queryset = User.objects.all().exclude(is_superuser=True)
    serializer_class = UserSerializer

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
