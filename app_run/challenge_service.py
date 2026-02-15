from django.db.models import Sum, QuerySet
from django.contrib.auth.models import User

from app_run.models import Run, Challenge


def create_challenge_ten_runs(athlete: User, queryset: QuerySet[Run]) -> None:
    """Создаёт достижение «Сделай 10 Забегов!» для атлета, если он совершил ровно 10 забегов.
    Функция проверяет количество забегов в переданном queryset. Если их ровно 10,
    автоматически создаётся объект Challenge с указанным названием и привязкой к атлету.
    Используется get_or_create для предотвращения дублирования достижений.
    """

    if queryset.count() == 10:
        Challenge.objects.get_or_create(full_name="Сделай 10 Забегов!", athlete=athlete)


def create_challenge_50_kilometers(athlete: User, queryset: QuerySet[Run]) -> None:
    """Создаёт достижение «Пробеги 50 километров!» для атлета, если суммарная дистанция его забегов >= 50 км.
    Функция вычисляет общую дистанцию всех забегов из переданного queryset. Если сумма
    составляет 50 километров или более, создаётся объект Challenge. Используется get_or_create
    для избежания дублирования."""

    total_distance = queryset.aggregate(Sum("distance"))["distance__sum"] or 0
    if total_distance >= 50:
        Challenge.objects.get_or_create(
            full_name="Пробеги 50 километров!", athlete=athlete
        )
