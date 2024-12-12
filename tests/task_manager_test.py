import pytest
import sqlite3
from datetime import datetime
from base_utils import Task, BaseManager, sync_with_search_db
from task_manager import TaskManager
from unittest.mock import patch


@pytest.fixture(scope="module")
def task_manager():
    """Создаем тестовый экземпляр TaskManager."""
    return TaskManager()


@pytest.fixture(scope="module")
def task_data():
    """Возвращаем данные для создания задачи."""
    return Task(
        task_id=0,  # ID 0, так как в базе он будет присвоен автоматически
        title="Тестовая задача",
        description="Описание задачи для теста",
        category="Тест",
        due_date="15.12.2024",
        priority="Высокий",
        status="Не выполнена",
    )


@pytest.fixture(autouse=True)  # Эта фикстура будет применяться ко всем тестам автоматически
def clean_database(task_manager):
    """Очищаем базу данных перед каждым тестом."""
    task_manager.cleanup_database()
    yield
    task_manager.cleanup_database()


def test_get_task(task_manager, task_data):
    """Тестируем получение задачи по ID."""
    task_id = task_manager.add_task(task_data)
    tasks = [
        Task(task_id=1, title="Написать отчет", description="Написать отчет по проекту до конца недели.",
             category="Работа", due_date="2023-10-15", priority="Высокий", status="Не выполнена"),

        Task(task_id=2, title="Купить продукты", description="Купить хлеб, молоко, яйца и фрукты.",
             category="Личные дела", due_date="2023-10-10", priority="Средний", status="Не выполнена"),

        Task(task_id=3, title="Сделать зарядку", description="Уделить 30 минут на утреннюю зарядку.",
             category="Здоровье", due_date="2023-10-08", priority="Низкий", status="Не выполнена"),

        Task(task_id=4, title="Подготовить презентацию", description="Подготовить презентацию для встреч.",
             category="Работа", due_date="2023-10-12", priority="Высокий", status="Не выполнена"),

        Task(task_id=5, title="Прочитать книгу", description="Прочитать 50 страниц книги для личного развития.",
             category="Образование", due_date="2023-10-20", priority="Низкий", status="Не выполнена"),
    ]
    task = task_manager.get_task(task_id)
    added_tasks_ids = [task_manager.add_task(task) for task in tasks]
    got_tasks = [task_manager.get_task(task_id) for task_id in added_tasks_ids]
    got_tasks_list = task_manager.get_task(added_tasks_ids)
    got_tasks_without_id = task_manager.get_task()
    with open("log.txt", "w", encoding="utf-8") as file:
        file.write(str(got_tasks_without_id))
    for test_task, retrieved_task in zip(tasks, got_tasks):
        assert retrieved_task.title.lower() == test_task.title
        assert retrieved_task.description.lower() == test_task.description
        assert retrieved_task.category.lower() == test_task.category
        assert retrieved_task.due_date.lower() == test_task.due_date
        assert retrieved_task.priority.lower() == test_task.priority
        assert retrieved_task.status.lower() == test_task.status
    assert len(tasks) == len(got_tasks_list)
    assert len(tasks) == len(got_tasks)
    assert len(got_tasks_without_id) == len(tasks) + 1
    assert task is not None
    assert task.task_id == task_id
    assert task.title == "Тестовая задача"


def test_create_task(task_manager, task_data):
    """Тестируем добавление задачи в базу данных."""
    task_id = task_manager.add_task(task_data)
    task = task_manager.get_task(task_id)
    assert task is not None
    assert task.title == "Тестовая задача".lower()
    assert task.description == "Описание задачи для теста".lower()
    assert task.category == "Тест".lower()
    assert task.due_date == "15.12.2024".lower()
    assert task.priority == "Высокий".lower()
    assert task.status == "Не выполнена".lower()


def test_update_task(task_manager, task_data):
    """Тестируем обновление задачи."""
    task_id = task_manager.add_task(task_data)
    updated_task = task_manager.update_task(task_id, title="Обновленная задача", status="Выполнена")
    updated_task_none = task_manager.update_task(000000, title="Обновленная задача", status="Выполнена")

    assert updated_task.title == "Обновленная задача"
    assert updated_task.status == "Выполнена"
    assert updated_task_none == 'Task not found'


def test_delete_task(task_manager, task_data):
    """Тестируем удаление задачи."""
    task_id = task_manager.add_task(task_data)
    task_manager.delete_task(task_id)
    task = task_manager.get_task(task_id)

    assert task is None


def test_search_task_by_keyword(task_manager, task_data):
    """Тестируем поиск задач по ключевому слову."""
    task_id = task_manager.add_task(task_data)
    search_results = task_manager.search_tasks(keyword="Тестовая задача")

    assert task_id in search_results


def test_search_task_by_category(task_manager, task_data):
    """Тестируем поиск задач по категории."""
    task_id = task_manager.add_task(task_data)
    search_results = task_manager.search_tasks(category="Тест")
    search_results_param = task_manager.search_tasks(keyword="Тестовая задача", category="Тест")
    search_results_param_status = task_manager.search_tasks(
        keyword="Тестовая задача", category="Тест", status="Не выполнена"
    )
    assert task_id in search_results_param
    assert task_id in search_results
    assert task_id in search_results_param_status


def test_sync_with_search_db(task_manager, task_data):
    """Тестируем синхронизацию между основной и поисковой базой данных."""
    task_id = task_manager.add_task(task_data)
    search_results = task_manager.search_tasks(keyword="Тестовая задача")

    assert task_id in search_results


def test_create_table(task_manager):
    """Тестируем создание таблицы задач."""
    with sqlite3.connect(task_manager.db_name) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks';")
        table = cursor.fetchone()

    assert table is not None and table[0] == 'tasks'


@patch("task_manager.TaskManager.add_task")
def test_add_task_with_mock(mock_add_task, task_data):
    """Тестируем добавление задачи с использованием mock."""
    mock_add_task.return_value = 1  # Задача с ID 1
    task_id = task_data.task_id
    task_data.task_id = mock_add_task(task_data)

    assert task_data.task_id == 1
