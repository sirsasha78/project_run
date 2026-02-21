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


def create_challenge_2_kilometers_in_10_minutes(athlete: User, run: Run) -> None:
    """Создаёт спортивное испытание для атлета, если он пробежал не менее 2 километров за 10 минут или быстрее.
    Функция проверяет дистанцию и время выполнения забега. Если условия выполняются — создаётся
    новое спортивное испытание с названием "2 километра за 10 минут!". Если такое испытание
    уже существует для данного атлета, повторное создание не происходит.
    Аргументы:
        athlete (User): Пользователь (атлет), который совершил забег. Должен быть экземпляром модели User.
        run (Run): Объект забега, содержащий информацию о дистанции и времени. Должен быть экземпляром модели Run.
    Примечания:
        - Дистанция проверяется в километрах (поле `distance` модели `Run`).
        - Время пересчитывается из секунд в минуты (поле `run_time_seconds` модели `Run`).
        - Используется `Challenge.objects.get_or_create()` для предотвращения дублирования испытаний.
    """

    distance = run.distance
    time_distance = run.run_time_seconds / 60
    if distance >= 2 and time_distance <= 10:
        Challenge.objects.get_or_create(
            full_name="2 километра за 10 минут!", athlete=athlete
        )
