from django.test import TestCase
from django.contrib.auth.models import User

from app_run.models import Run


class RunModelTests(TestCase):
    """Тесты для модели Run.
    Этот класс содержит юнит-тесты, проверяющие корректность создания
    и получения данных модели Run. Проверяются поля объекта, а также
    значения по умолчанию для некоторых полей. Каждый тест выполняется
    в изолированной среде, обеспечиваемой Django TestCase."""

    def setUp(self):
        """Подготовка тестовых данных перед выполнением каждого теста.
        Создаёт тестового пользователя и один объект модели Run,
        который используется во всех тестовых методах для проверки
        корректности работы модели."""

        self.user = User.objects.create_user(username="Петр", password="123456")
        self.first_run = Run.objects.create(athlete=self.user, comment="test_comment")

    def test_create_run(self):
        """Проверяет успешное создание экземпляра модели Run.
        Убеждается, что объект self.first_run действительно является
        экземпляром класса Run, подтверждая корректность создания объекта."""

        self.assertIsInstance(self.first_run, Run)

    def test_str_representation(self):
        """Проверяет строковое представление объекта Run."""

        self.assertEqual(
            str(self.first_run),
            f"Забег - {self.first_run.created_at} - {self.first_run.athlete.username}",
        )

    def test_retrieving_run(self):
        """Проверяет корректность сохранённых данных в объекте Run."""

        self.assertEqual(self.first_run.athlete.username, "Петр")
        self.assertEqual(self.first_run.comment, "test_comment")
        self.assertEqual(self.first_run.status, "init")
        self.assertEqual(self.first_run.distance, 0.0)
        self.assertEqual(self.first_run.run_time_seconds, 0)
        self.assertEqual(self.first_run.speed, 0.0)

    def test_saving_run(self):
        """Проверяет сохранение нового объекта Run с заданными параметрами.
        Создаёт второго пользователя и новый объект Run с заполненными полями:
        статус, дистанция, время и скорость. Сохраняет объект в базу данных."""

        user2 = User.objects.create(username="Вася", password=123456)
        second_run = Run()
        second_run.athlete = user2
        second_run.status = "in_progress"
        second_run.distance = 5.0
        second_run.run_time_seconds = 600
        second_run.speed = 2.0
        second_run.save()

        all_runs = Run.objects.all()
        self.assertEqual(all_runs.count(), 2)
        self.assertEqual(second_run.comment, None)
        self.assertEqual(second_run.status, "in_progress")
        self.assertEqual(second_run.distance, 5.0)
        self.assertEqual(second_run.run_time_seconds, 600)
        self.assertEqual(second_run.speed, 2.0)
