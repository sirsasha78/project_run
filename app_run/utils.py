from datetime import datetime
from django.contrib.auth.models import User
from django.db.models import Min, Max
from geopy.distance import geodesic


from app_run.models import Position, Run
from artifacts.models import CollectibleItem


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


def check_and_collect_artifacts(user: User, latitude: float, longitude: float) -> None:
    """Проверяет, находится ли пользователь в радиусе 100 метров от любого из коллекционных предметов,
    и добавляет эти предметы в инвентарь пользователя.
    Функция перебирает все доступные коллекционные предметы в базе данных, вычисляет расстояние
    между текущими координатами пользователя и координатами каждого предмета с использованием
    геодезического расстояния, и если расстояние не превышает 100 метров, добавляет предмет
    в список собранных пользователем объектов."""

    items = CollectibleItem.objects.all().only("id", "latitude", "longitude")
    for item in items:
        start = (latitude, longitude)
        end = (item.latitude, item.longitude)
        distance = geodesic(start, end).meters
        if distance <= 100:
            user.items.add(item)


def calculate_run_time_seconds(run: Run) -> int:
    """Вычисляет продолжительность забега в секундах на основе временных меток позиций.
    Функция определяет минимальное и максимальное значения времени из всех позиций
    указанного забега (объект `Run`), вычисляет разницу между ними и возвращает
    продолжительность в секундах. Если отсутствуют временные данные, возвращается 0."""

    times = run.positions.aggregate(
        min_time=Min("date_time"), max_time=Max("date_time")
    )
    min_time = times["min_time"]
    max_time = times["max_time"]

    if not min_time or not max_time:
        return 0

    duration = max_time - min_time
    return int(duration.total_seconds())


def calculate_speed(
    run: Run, current_time: datetime, latitude: float, longitude: float
) -> float:
    """Вычисляет текущую скорость движения на основе последней зафиксированной позиции и новых координат.

    Скорость рассчитывается как отношение расстояния между двумя точками к разнице во времени
    между моментом фиксации предыдущей позиции и текущим временем. Расстояние вычисляется
    с использованием геодезического метода (точный расчёт по кривизне Земли).
    Примечания:
        - Функция использует метод `geodesic` из библиотеки `geopy` для точного расчёта
          расстояния между двумя точками на поверхности Земли.
        - Если в `run.positions` нет ни одной записи или поле `date_time` пустое,
          скорость будет установлена в 0.0.
        - При нулевой или отрицательной разнице во времени (например, при ошибках в данных)
          возвращается 0.0, чтобы избежать деления на ноль или некорректных значений."""

    previous_position = run.positions.order_by("-date_time").first()

    if previous_position and previous_position.date_time:
        start = (previous_position.latitude, previous_position.longitude)
        end = (latitude, longitude)
        distance = geodesic(start, end).meters
        time_diff = (current_time - previous_position.date_time).total_seconds()
        if time_diff > 0:
            speed = round(distance / time_diff, 2)
        else:
            speed = 0.0
    else:
        speed = 0.0
    return speed
