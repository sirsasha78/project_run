from geopy.distance import geodesic
from app_run.models import Position


def calculate_run_distance(positions: list[Position]) -> float:
    """Вычисляет суммарное расстояние маршрута по списку геопозиций.
    Функция принимает упорядоченный список объектов позиций (например, зафиксированных
    во время бега) и вычисляет общее пройденное расстояние между последовательными
    точками с использованием геодезического расстояния (по дуге земной поверхности).
    Если передано менее двух позиций, возвращается нулевое расстояние, так как
    невозможно определить маршрут.
    Замечания:
        - Для вычисления расстояния используется функция `geodesic` из библиотеки `geopy`,
          обеспечивающая высокую точность за счёт учёта кривизны Земли.
        - Координаты должны быть указаны в десятичных градусах.
        - Результат всегда неотрицательный."""

    distance = 0.0
    if len(positions) < 2:
        return 0.0
    for i in range(len(positions) - 1):
        start = (positions[i].latitude, positions[i].longitude)
        end = (positions[i + 1].latitude, positions[i + 1].longitude)
        distance += geodesic(start, end).kilometers
    return round(distance, 3)
