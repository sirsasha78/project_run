from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from django.db.models import QuerySet


class CustomPagination(PageNumberPagination):
    """Класс пользовательской пагинации для управления постраничным выводом данных.
    Этот класс наследуется от `PageNumberPagination` и предоставляет возможность клиенту API
    указывать желаемое количество элементов на странице с помощью параметра `size` в URL-запросе.
    Если параметр `size` не передан, пагинация отключается, и данные возвращаются без разбиения на страницы.
    Атрибуты:
        page_size_query_param (str): Название параметра в URL, через который клиент может
            задать размер страницы. По умолчанию — 'size'."""

    page_size_query_param = "size"

    def paginate_queryset(
        self, queryset: QuerySet, request: Request, view=None
    ) -> None | QuerySet:
        """Определяет, должна ли выполняться пагинация, и возвращает paginated queryset.
        Метод проверяет, присутствует ли в запросе параметр `size`. Если параметр отсутствует,
        пагинация не применяется, и метод возвращает None, что означает, что данные должны быть
        возвращены как есть. Если параметр присутствует, вызывается стандартная логика пагинации.
        """

        if self.page_size_query_param not in request.query_params:
            return None
        return super().paginate_queryset(queryset, request, view)
