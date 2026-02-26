from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from app_run.models import Run, Challenge


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
