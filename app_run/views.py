from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from rest_framework import status
from django.conf import settings

from app_run.models import Run
from app_run.serializers import RunSerializer


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
