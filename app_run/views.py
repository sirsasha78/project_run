from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.conf import settings


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
