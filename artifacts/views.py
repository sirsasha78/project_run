from rest_framework import viewsets

from artifacts.models import CollectibleItem
from artifacts.serializers import CollectibleItemSerializer


class CollectibleItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Набор представлений для отображения коллекционных предметов.
    Предоставляет только операции чтения (просмотр одного или списка объектов)
    для модели CollectibleItem. Используется для безопасного доступа к данным
    без возможности их изменения через API.
    Атрибуты:
        queryset (QuerySet): Набор объектов модели CollectibleItem,
            доступных для просмотра.
        serializer_class (Serializer): Класс сериализатора, используемый
            для преобразования объектов модели в JSON и обратно."""

    queryset = CollectibleItem.objects.all()
    serializer_class = CollectibleItemSerializer
