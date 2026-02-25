from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from app_run.models import Run


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
