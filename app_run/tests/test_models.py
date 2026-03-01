from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError

from app_run.models import Run, AthleteInfo, Challenge, Position, Subscribe


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


class AthleteInfoModelTests(TestCase):
    """Набор тестов для модели AthleteInfo.
    Этот класс тестирует функциональность модели AthleteInfo, включая:
    - Создание экземпляра модели
    - Строковое представление объекта
    - Получение значений полей по умолчанию
    - Сохранение и извлечение данных из базы данных
    Атрибуты:
        athlete (User): Пользователь, созданный для тестов, представляющий спортсмена.
        athleteinfo (AthleteInfo): Объект модели AthleteInfo, связанный с тестовым пользователем.
    """

    def setUp(self):
        """Подготавливает данные для выполнения тестов.
        Создаёт тестового пользователя (спортсмена) и связанный с ним объект AthleteInfo.
        Выполняется перед каждым тестовым методом."""

        self.athlete = User.objects.create_user(username="Петр", password="123456")
        self.athleteinfo = AthleteInfo.objects.create(athlete=self.athlete)

    def test_create_athleteInfo(self):
        """Проверяет корректность создания экземпляра модели AthleteInfo.
        Убеждается, что созданный объект athleteinfo является экземпляром класса AthleteInfo.
        """

        self.assertIsInstance(self.athleteinfo, AthleteInfo)

    def test_str_representation(self):
        """Проверяет строковое представление объекта AthleteInfo.
        Убеждается, что метод __str__ возвращает ожидаемую строку формата:
        'Информация о спортсмене - {username}'."""

        self.assertEqual(
            str(self.athleteinfo), f"Информация о спортсмене - {self.athlete.username}"
        )

    def test_retrieving_athleteinfo(self):
        """Проверяет корректность получения значений полей объекта AthleteInfo.
        Убеждается, что поля goals и weight имеют значение None по умолчанию,
        а поле athlete правильно ссылается на созданного пользователя."""

        self.assertEqual(self.athleteinfo.goals, None)
        self.assertEqual(self.athleteinfo.weight, None)
        self.assertEqual(self.athleteinfo.athlete, self.athlete)

    def test_saving_athleteinfo(self):
        """Проверяет возможность сохранения и извлечения объекта AthleteInfo из базы данных.
        Создаёт второго пользователя и связанный с ним объект AthleteInfo с заполненными полями.
        Сохраняет объект и проверяет:
        - Общее количество записей в базе данных стало равно 2
        - Поля goals, weight и athlete содержат ожидаемые значения"""

        athlete2 = User.objects.create_user(username="Вася", password="1234")
        athleteinfo2 = AthleteInfo()
        athleteinfo2.goals = "Пробежать 10 км."
        athleteinfo2.weight = 78
        athleteinfo2.athlete = athlete2
        athleteinfo2.save()

        all_athleteinfo = AthleteInfo.objects.all()
        self.assertEqual(all_athleteinfo.count(), 2)
        self.assertEqual(athleteinfo2.goals, "Пробежать 10 км.")
        self.assertEqual(athleteinfo2.weight, 78)
        self.assertEqual(athleteinfo2.athlete, athlete2)


class ChallengeModelTests(TestCase):
    """Тесты для модели Challenge.
    Проверяет корректность создания, сохранения и строкового
    представления объектов модели Challenge. Использует тестовый
    фреймворк Django для проверки бизнес-логики и взаимодействия
    с базой данных."""

    def setUp(self):
        """Подготавливает данные для тестов.
        Создаёт тестового пользователя (атлета) и одно испытание (challenge),
        которые будут использоваться во всех методах тест-кейса."""

        self.athlete = User.objects.create_user(username="Петр", password="123456")
        self.challenge = Challenge.objects.create(
            full_name="Сделай 10 Забегов!", athlete=self.athlete
        )

    def test_str_representation(self):
        """Проверяет строковое представление объекта Challenge.
        Убеждается, что метод __str__ возвращает корректную строку
        формата 'Испытание атлета {username}', где username — имя владельца испытания.
        """

        self.assertEqual(
            str(self.challenge), f"Испытание атлета {self.athlete.username}"
        )

    def test_retrieving_challenge(self):
        """Проверяет корректность извлечения данных объекта Challenge.
        Убеждается, что поля full_name и athlete были правильно сохранены
        и соответствуют ожидаемым значениям после создания объекта."""

        self.assertEqual(self.challenge.full_name, "Сделай 10 Забегов!")
        self.assertEqual(self.challenge.athlete.username, "Петр")

    def test_saving_challenge(self):
        """Проверяет корректность сохранения нового объекта Challenge в БД.
        Создаёт второе испытание с другим атлетом и проверяет:
        - Общее количество записей в базе стало равно 2,
        - Новое испытание содержит правильное название,
        - Новое испытание привязано к правильному атлету."""

        challenge2 = Challenge()
        athlete2 = User.objects.create_user(username="Вася", password="123456")
        challenge2.full_name = "Пробеги 50 километров!"
        challenge2.athlete = athlete2
        challenge2.save()

        all_challenges = Challenge.objects.all()
        self.assertEqual(all_challenges.count(), 2)
        self.assertEqual(challenge2.full_name, "Пробеги 50 километров!")
        self.assertEqual(challenge2.athlete, athlete2)


class PositionModelTests(TestCase):
    """Тесты для модели Position.
    Проверяет корректность создания, сохранения и строкового представления
    объектов позиции (Position), а также их привязку к забегу (Run) и участнику (User).
    """

    def setUp(self):
        """Подготавливает данные для тестов.
        Создаёт:
        - Пользователя-спортсмена с именем "Петр",
        - Забег (Run), связанный с этим спортсменом,
        - Позицию (Position) с заданными координатами, привязанную к забегу."""

        self.athlete = User.objects.create_user(username="Петр", password="123456")
        self.run = Run.objects.create(athlete=self.athlete)
        self.position = Position.objects.create(
            run=self.run, latitude=45.23, longitude=123.12
        )

    def test_str_representation(self):
        """Проверяет строковое представление объекта Position.
        Убеждается, что метод __str__ возвращает строку в формате:
        'Координаты - <имя_пользователя>'."""

        self.assertEqual(
            str(self.position), f"Координаты - {self.run.athlete.username}"
        )

    def test_retrieving_position(self):
        """Проверяет корректность извлечения данных позиции.
        Убеждается, что:
        - Позиция правильно привязана к забегу,
        - Широта и долгота соответствуют заданным значениям,
        - Время (date_time) по умолчанию равно None,
        - Скорость (speed) и дистанция (distance) инициализированы нулевыми значениями.
        """

        self.assertEqual(self.position.run, self.run)
        self.assertEqual(self.position.latitude, 45.23)
        self.assertEqual(self.position.longitude, 123.12)
        self.assertEqual(self.position.date_time, None)
        self.assertEqual(self.position.speed, 0.0)
        self.assertEqual(self.position.distance, 0.0)

    def test_saving_position(self):
        """Проверяет корректность сохранения новой позиции в базу данных.
        Создаёт вторую позицию с другим спортсменом и параметрами,
        сохраняет её и проверяет:
        - Общее количество позиций в базе стало равно 2,
        - Все поля новой позиции сохранены корректно."""

        position2 = Position()
        athlete2 = User.objects.create_user(username="Вася", password="123456")
        run2 = Run.objects.create(athlete=athlete2)
        position2.run = run2
        position2.latitude = 52.12
        position2.longitude = 132.22
        position2.speed = 5.0
        position2.distance = 12.2
        position2.save()

        all_positions = Position.objects.all()
        self.assertEqual(all_positions.count(), 2)
        self.assertEqual(position2.run, run2)
        self.assertEqual(position2.latitude, 52.12)
        self.assertEqual(position2.longitude, 132.22)
        self.assertEqual(position2.speed, 5.0)
        self.assertEqual(position2.distance, 12.2)


class SubscribeModelTests(TestCase):
    """Тесты для модели Subscribe, проверяющие её корректное поведение.
    Класс содержит тесты для проверки:
    - Строкового представления объекта подписки.
    - Возможности получения данных подписки из базы.
    - Корректности сохранения новой подписки в базу данных.
    Атрибуты:
        athlete (User): Пользователь, выступающий в роли атлета.
        coach (User): Пользователь, выступающий в роли тренера.
        subscribe (Subscribe): Объект подписки, созданный для тестов."""

    def setUp(self):
        """Подготавливает данные для тестов.
        Создаёт двух пользователей: атлета и тренера, а также объект подписки,
        связывающий их. Выполняется перед каждым тестовым методом."""

        self.athlete = User.objects.create_user(username="Петр", password="123456")
        self.coach = User.objects.create_user(username="Василий", password="123456")
        self.subscribe = Subscribe.objects.create(
            athlete=self.athlete, coach=self.coach
        )

    def test_str_representation(self):
        """Проверяет строковое представление объекта подписки.
        Убеждается, что метод __str__ возвращает корректную строку формата:
        'Подписка на тренера {имя_тренера} от атлета {имя_атлета}'."""

        self.assertEqual(
            str(self.subscribe),
            f"Подписка на тренера {self.coach.username} от атлета {self.athlete.username}",
        )

    def test_retrieving_subscribe(self):
        """Проверяет корректность извлечения данных подписки из базы.
        Убеждается, что поля объекта подписки соответствуют ожидаемым значениям:
        - Имя атлета — "Петр".
        - Имя тренера — "Василий".
        - Статус подписки (is_subscribed) — False (по умолчанию)."""

        self.assertEqual(self.subscribe.athlete.username, "Петр")
        self.assertEqual(self.subscribe.coach.username, "Василий")
        self.assertEqual(self.subscribe.is_subscribed, False)

    def test_unique_constraint(self):
        """Проверяет, что нельзя подписаться дважды на одного тренера."""

        self.assertRaises(
            IntegrityError,
            lambda: Subscribe.objects.create(athlete=self.athlete, coach=self.coach),
        )

    def test_saving_subscribe(self):
        """Проверяет корректность сохранения новой подписки в базу данных.
        Создаёт нового атлета и тренера, формирует новую подписку с is_subscribed=True,
        сохраняет её и проверяет:
        - Общее количество подписок в базе стало равно 2.
        - Сохранённые значения атлета, тренера и статуса соответствуют заданным."""

        subscribe2 = Subscribe()
        athlete2 = User.objects.create_user(username="Иван", password="123456")
        coach2 = User.objects.create_user(username="Андрей", password="123456")
        subscribe2.athlete = athlete2
        subscribe2.coach = coach2
        subscribe2.is_subscribed = True
        subscribe2.save()

        all_subscribes = Subscribe.objects.all()
        self.assertEqual(all_subscribes.count(), 2)
        self.assertEqual(subscribe2.athlete, athlete2)
        self.assertEqual(subscribe2.coach, coach2)
        self.assertEqual(subscribe2.is_subscribed, True)
