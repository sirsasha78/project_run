from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from app_run.models import Run, Challenge, Position


class RunListViewTests(TestCase):
    """Набор тестов для проверки функциональности представлений модели Run.
    Тесты охватывают операции CRUD (создание, чтение, обновление, удаление)
    через API для объектов Run. Используется Django TestCase с APIClient
    для имитации запросов к эндпоинтам.
    Атрибуты:
        client (APIClient): Клиент для выполнения HTTP-запросов.
        user (User): Пользователь, создающийся перед запуском тестов.
        test_run1 (Run): Первый тестовый забег с базовыми данными.
        test_run2 (Run): Второй тестовый забег с дополнительными полями."""

    def setUp(self):
        """Инициализация тестовых данных перед каждым тестом.
        Создаёт:
            - Экземпляр APIClient.
            - Пользователя с именем "Петр".
            - Два тестовых забега, связанных с пользователем."""

        self.client = APIClient()
        self.user = User.objects.create(username="Петр", password="123456")
        self.test_run1 = Run.objects.create(athlete=self.user, comment="test_comment")
        self.test_run2 = Run.objects.create(
            athlete=self.user,
            status="in_progress",
            distance=2.0,
            run_time_seconds=600,
            speed=6.0,
        )

    def test_get_list(self):
        """Проверяет получение списка всех забегов.
        Отправляет GET-запрос к эндпоинту 'run-list' и проверяет:
            - Статус ответа 200 OK.
            - В ответе содержатся данные двух созданных забегов."""

        url = reverse("run-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_detail(self):
        """Проверяет получение детальной информации о конкретном забеге.
        Отправляет GET-запрос к эндпоинту 'run-detail' для первого забега.
        Проверяет:
            - Статус ответа 200 OK.
            - Поле 'comment' совпадает с ожидаемым значением.
            - Поле 'status' имеет значение по умолчанию 'init'."""

        url = reverse("run-detail", kwargs={"pk": self.test_run1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["comment"], "test_comment")
        self.assertEqual(response.data["status"], "init")

    def test_post_create(self):
        """Проверяет создание нового забега через POST-запрос.
        Отправляет данные на эндпоинт 'run-list' и проверяет:
            - Статус ответа 201 Created.
            - Общее количество забегов увеличилось до 3.
            - Созданный забег имеет корректные значения полей."""

        url = reverse("run-list")
        data = {
            "athlete": self.user.pk,
            "comment": "new_comment",
            "status": "in_progress",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Run.objects.count(), 3)
        new_run = Run.objects.get(comment="new_comment")
        self.assertEqual(new_run.status, "in_progress")

    def test_put_update(self):
        """Проверяет полное обновление существующего забега через PUT-запрос.
        Отправляет обновлённые данные на эндпоинт 'run-detail' второго забега.
        Проверяет:
            - Статус ответа 200 OK.
            - После обновления поля 'status' и 'distance' имеют новые значения."""

        url = reverse("run-detail", kwargs={"pk": self.test_run2.pk})
        data = {
            "athlete": self.user.pk,
            "status": "init",
            "distance": 5.0,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_run2.refresh_from_db()
        self.assertEqual(self.test_run2.status, "init")
        self.assertEqual(self.test_run2.distance, 5.0)

    def test_delete_destroy(self):
        """Проверяет удаление забега через DELETE-запрос.
        Отправляет запрос на удаление второго забега и проверяет:
            - Статус ответа 204 No Content.
            - В базе остаётся только один забег."""

        url = reverse("run-detail", kwargs={"pk": self.test_run2.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Run.objects.count(), 1)


class ChallengesSummaryViewTests(TestCase):
    """Набор тестов для проверки функциональности представления ChallengesSummaryView.
    Тесты обеспечивают корректность отображения сводной информации о челленджах,
    включая количество участников и названия челленджей. Проверяется, что данные
    возвращаются в правильном формате и соответствуют ожидаемым значениям.
    Атрибуты:
        client (APIClient): Клиент для выполнения HTTP-запросов.
        user1 (User): Первый тестовый пользователь.
        user2 (User): Второй тестовый пользователь.
        user3 (User): Третий тестовый пользователь.
        challenge1 (Challenge): Первый тестовый челлендж.
        challenge2 (Challenge): Второй тестовый челлендж с тем же названием, что и у первого.
        challenge3 (Challenge): Третий тестовый челлендж с уникальным названием."""

    def setUp(self):
        """Подготавливает данные для выполнения каждого теста.
        Создаёт клиент API и несколько пользователей, а также три челленджа,
        два из которых имеют одинаковое название и привязаны к разным пользователям.
        Это позволяет проверить группировку участников по названию челленджа."""

        self.client = APIClient()
        self.user1 = User.objects.create(username="Петр", password=1234)
        self.user2 = User.objects.create(username="Иван", password=1234)
        self.user3 = User.objects.create(username="Вася", password=1234)
        self.challenge1 = Challenge.objects.create(
            full_name="Пробеги 50 километров!", athlete=self.user1
        )
        self.challenge2 = Challenge.objects.create(
            full_name="Пробеги 50 километров!", athlete=self.user2
        )
        self.challenge3 = Challenge.objects.create(
            full_name="2 километра за 10 минут!", athlete=self.user3
        )

    def test_get_list(self):
        """Проверяет корректность работы GET-запроса к эндпоинту 'challenges-summary'.
        Выполняет запрос к представлению и убеждается, что:
        - Статус ответа — 200 OK.
        - Возвращается два уникальных челленджа.
        - Названия челленджей совпадают с ожидаемыми.
        - У первого челленджа два участника, так как он создан для двух пользователей.
        """

        url = reverse("challenges-summary")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name_to_display"], "Пробеги 50 километров!")
        self.assertEqual(
            response.data[1]["name_to_display"], "2 километра за 10 минут!"
        )
        self.assertEqual(len(response.data[0]["athletes"]), 2)


class UserListViewTests(TestCase):
    """Набор тестов для проверки представлений списка и детальной информации пользователей.
    Тесты охватывают:
    - Получение списка всех пользователей.
    - Получение детальной информации об атлете.
    - Получение детальной информации о тренере.
    Атрибуты:
        client (APIClient): Клиент для выполнения HTTP-запросов.
        athlete (User): Пользователь с правами атлета (is_staff=False).
        coach (User): Пользователь с правами тренера (is_staff=True)."""

    def setUp(self):
        """Инициализация тестовых данных перед каждым тестом.
        Создаёт:
            - Экземпляр APIClient для отправки запросов.
            - Пользователя-атлета с именем "Петр".
            - Пользователя-тренера с именем "Иван"."""

        self.client = APIClient()
        self.athlete = User.objects.create_user(
            username="Петр", password="123456", is_staff=False
        )
        self.coach = User.objects.create_user(
            username="Иван", password="123456", is_staff=True
        )

    def test_get_list(self):
        """Проверяет, что эндпоинт получения списка пользователей работает корректно.
        Ожидаемое поведение:
            - Возвращается статус 200 OK.
            - В ответе содержатся данные обоих созданных пользователей (длина списка — 2).
        """

        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_detail_athlete(self):
        """Проверяет получение детальной информации об атлете.
        Ожидаемое поведение:
            - Возвращается статус 200 OK.
            - Имя пользователя в ответе — "Петр".
            - Тип пользователя определяется как "athlete"."""

        url = reverse("user-detail", kwargs={"pk": self.athlete.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "Петр")
        self.assertEqual(response.data["type"], "athlete")
        self.assertEqual(response.data["runs_finished"], 0)
        self.assertEqual(response.data["rating"], None)

    def test_get_detail_coach(self):
        """Проверяет получение детальной информации о тренере.
        Ожидаемое поведение:
            - Возвращается статус 200 OK.
            - Имя пользователя в ответе — "Иван".
            - Тип пользователя определяется как "coach"."""

        url = reverse("user-detail", kwargs={"pk": self.coach.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "Иван")
        self.assertEqual(response.data["type"], "coach")

    def test_superuser_not_included_in_list(self):
        """Проверяет, что суперпользователь не включён в список пользователей.
        Ожидаемое поведение:
            - Созданный суперпользователь отсутствует в данных ответа при запросе списка пользователей.
        Тест создаёт суперпользователя с заданными учётными данными,
        затем выполняет GET-запрос к эндпоинту 'user-list'. Убеждается,
        что объект суперпользователя не присутствует среди данных ответа."""

        superuser = User.objects.create_superuser(
            username="admin", email="admin@mail.ru", password="123456"
        )
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertNotIn(superuser, response.data)

    def test_filter_users_by_type_athlete(self):
        """Проверяет фильтрацию пользователей по типу 'athlete'.
        Ожидаемое поведение:
            - Возвращается статус 200 OK.
            - В ответе содержится ровно один пользователь.
            - Имя этого пользователя — "Петр".
        Тест отправляет GET-запрос к эндпоинту 'user-list' с параметром фильтрации '?type=athlete'.
        Проверяет, что в ответе содержится только один пользователь указанного типа
        и его имя соответствует ожидаемому."""

        url = reverse("user-list") + "?type=athlete"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["username"], "Петр")

    def test_filter_users_by_type_coach(self):
        """Проверяет фильтрацию пользователей по типу 'coach'.
        Ожидаемое поведение:
            - Возвращается статус 200 OK.
            - В ответе содержится ровно один пользователь.
            - Имя этого пользователя — "Иван".
        Тест отправляет GET-запрос к эндпоинту 'user-list' с параметром фильтрации '?type=coach'.
        Проверяет, что в ответе содержится только один пользователь указанного типа
        и его имя соответствует ожидаемому."""

        url = reverse("user-list") + "?type=coach"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["username"], "Иван")


class StartViewTests(TestCase):
    """Набор тестов для проверки функциональности запуска забега через представление `start-run`.
    Тесты охватывают различные сценарии:
    - Успешный старт забега
    - Попытка начать уже запущенный забег
    - Попытка начать завершённый забег
    - Попытка начать несуществующий забег
    Атрибуты:
        client (APIClient): Клиент для выполнения HTTP-запросов.
        athlete (User): Пользователь (спортсмен), создаётся для тестов.
        test_run (Run): Объект забега, связанный со спортсменом."""

    def setUp(self):
        """Инициализация тестовых данных перед каждым тестом.
        Создаёт:
            - Экземпляр APIClient для имитации запросов.
            - Пользователя с именем "Петр" и паролем "123456".
            - Забег, привязанный к этому пользователю."""

        self.client = APIClient()
        self.athlete = User.objects.create_user(username="Петр", password="123456")
        self.test_run = Run.objects.create(athlete=self.athlete)

    def test_start_run_success(self):
        """Проверяет успешный запуск забега.
        Отправляет POST-запрос на URL `start-run` с идентификатором забега.
        Ожидается:
            - Статус ответа 200 OK.
            - Сообщение в теле ответа: "Забег начат".
            - Статус забега в базе данных изменяется на "в процессе"."""

        url = reverse("start-run", kwargs={"run_id": self.test_run.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "Забег начат")
        self.test_run.refresh_from_db()
        self.assertEqual(self.test_run.status, Run.RUN_STATUS_IN_PROGRESS)

    def test_start_run_already_started(self):
        """Проверяет реакцию на попытку запуска уже начатого забега.
        Предусловие: статус забега установлен в "в процессе".
        Ожидается:
            - Статус ответа 400 Bad Request."""

        self.test_run.status = Run.RUN_STATUS_IN_PROGRESS
        self.test_run.save()
        url = reverse("start-run", kwargs={"run_id": self.test_run.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_start_run_already_finished(self):
        """Проверяет реакцию на попытку запуска завершённого забега.
        Предусловие: статус забега установлен в "завершён".
        Ожидается:
            - Статус ответа 400 Bad Request."""

        self.test_run.status = Run.RUN_STATUS_FINISHED
        self.test_run.save()
        url = reverse("start-run", kwargs={"run_id": self.test_run.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_start_run_not_found(self):
        """Проверяет реакцию на попытку запуска несуществующего забега.
        Используется несуществующий идентификатор (4).
        Ожидается:
            - Статус ответа 404 Not Found."""

        url = reverse("start-run", kwargs={"run_id": 4})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FinishViewTests(TestCase):
    """Набор тестов для проверки функциональности завершения забега через представление `stop-run`.
    Тесты охватывают различные сценарии:
    - Успешное завершение забега.
    - Попытку завершить забег в недопустимых состояниях (например, инициализирован или уже завершён).
    - Обработку несуществующего забега.
    - Расчёт дистанции и времени забега при завершении.
    - Создание испытания после 10-го завершённого забега."""

    def setUp(self):
        """Подготовка данных перед выполнением каждого теста.
        Создаёт:
        - Экземпляр клиента API.
        - Пользователя-спортсмена с именем "Петр".
        - Забег со статусом "в процессе" для этого спортсмена."""

        self.client = APIClient()
        self.athlete = User.objects.create_user(username="Петр", password="123456")
        self.test_run = Run.objects.create(
            athlete=self.athlete, status=Run.RUN_STATUS_IN_PROGRESS
        )

    def test_finished_run_success(self):
        """Проверяет успешное завершение забега.
        Отправляет POST-запрос на завершение забега и проверяет:
        - Код ответа 200 OK.
        - Сообщение в ответе: "Забег закончен".
        - Статус забега в базе данных изменён на "завершён"."""

        url = reverse("stop-run", kwargs={"run_id": self.test_run.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "Забег закончен")
        self.test_run.refresh_from_db()
        self.assertEqual(self.test_run.status, Run.RUN_STATUS_FINISHED)

    def test_finished_run_already_init(self):
        """Проверяет, что нельзя завершить забег со статусом "инициализирован".
        Изменяет статус забега на INIT, отправляет запрос на завершение и проверяет:
        - Код ответа 400 Bad Request."""

        self.test_run.status = Run.RUN_STATUS_INIT
        self.test_run.save()
        url = reverse("stop-run", kwargs={"run_id": self.test_run.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_finished_already_finished(self):
        """Проверяет, что нельзя повторно завершить уже завершённый забег.
        Устанавливает статус забега как "завершён", отправляет запрос и проверяет:
        - Код ответа 400 Bad Request."""

        self.test_run.status = Run.RUN_STATUS_FINISHED
        self.test_run.save()
        url = reverse("stop-run", kwargs={"run_id": self.test_run.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_finished_run_not_found(self):
        """Проверяет обработку запроса на завершение несуществующего забега.
        Отправляет запрос с несуществующим ID и проверяет:
        - Код ответа 404 Not Found."""

        url = reverse("stop-run", kwargs={"run_id": 4})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_run_distance_is_calculated_on_finish(self):
        """Проверяет, что дистанция забега корректно рассчитывается при завершении.
        Добавляет две позиции с координатами и временной разницей,
        завершает забег и проверяет, что поле distance больше нуля."""

        now = timezone.now()
        Position.objects.create(
            run=self.test_run,
            latitude=55.7558,
            longitude=37.6176,
            date_time=now - timezone.timedelta(minutes=10),
        )
        Position.objects.create(
            run=self.test_run, latitude=55.7568, longitude=37.6176, date_time=now
        )
        url = reverse("stop-run", kwargs={"run_id": self.test_run.pk})
        self.client.post(url)
        self.test_run.refresh_from_db()
        self.assertGreater(self.test_run.distance, 0)

    def test_run_time_seconds_is_calculated_on_finish(self):
        """Проверяет, что продолжительность забега в секундах корректно рассчитывается при завершении.
        Добавляет две позиции с интервалом в 10 минут, завершает забег и проверяет:
        - Время забега больше 500 секунд."""

        now = timezone.now()
        Position.objects.create(
            run=self.test_run,
            latitude=55.7558,
            longitude=37.6176,
            date_time=now - timezone.timedelta(minutes=10),
        )
        Position.objects.create(
            run=self.test_run, latitude=55.7568, longitude=37.6176, date_time=now
        )
        url = reverse("stop-run", kwargs={"run_id": self.test_run.pk})
        self.client.post(url)
        self.test_run.refresh_from_db()
        self.assertGreater(self.test_run.run_time_seconds, 500)

    def test_create_challenge_ten_runs_on_10th_finished_run(self):
        """Проверяет создание испытания 'Сделай 10 Забегов!' после 10-го завершённого забега.
        Создаёт 9 завершённых забегов, затем завершает 10-й (test_run),
        после чего проверяет наличие соответствующего испытания в базе данных."""

        for _ in range(9):
            Run.objects.create(athlete=self.athlete, status=Run.RUN_STATUS_FINISHED)

        url = reverse("stop-run", kwargs={"run_id": self.test_run.pk})
        self.client.post(url)
        challenge_exists = Challenge.objects.filter(
            full_name="Сделай 10 Забегов!", athlete=self.athlete
        ).exists()
        self.assertTrue(challenge_exists)
