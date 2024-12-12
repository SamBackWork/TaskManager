import pytest
from datetime import datetime
from task_manager import TaskManager, Task
from commands import Commands  # импортируйте ваш модуль с классом Commands


@pytest.fixture
def setup_task_manager():
    """Создание нового экземпляра TaskManager для тестирования."""
    return TaskManager()


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


@pytest.fixture
def sample_task_data():
    """Предоставление примерных данных для задачи."""
    return {
        "title": "Тестовая задача",
        "description": "Описание тестовой задачи",
        "due_date": "01.01.2024",
        "category": "Работа",
        "priority": "Низкий",
        "status": "Новая"
    }


def test_create_task(setup_task_manager, sample_task_data, monkeypatch):
    """Тестирование создания задачи."""
    monkeypatch.setattr('builtins.input', lambda _: sample_task_data.get('title') or sample_task_data.get(
        'description') or sample_task_data.get('due_date') or sample_task_data.get('category'))

    task_id = Commands.create_task_from_input()
    task = setup_task_manager.get_task(task_id)

    assert task.title == sample_task_data['title']
    assert task.description == sample_task_data['description']
    assert task.due_date == datetime.strptime(sample_task_data['due_date'], '%d.%m.%Y')
    assert task.category == sample_task_data['category']
    assert task.status == "Новая"


def test_update_task(setup_task_manager, monkeypatch):
    # Создаем задачу для обновления
    task_id = setup_task_manager.add_task(tasks[0])

    # Эмулирование последовательного ввода пользователя: выбор поля, новое значение и выход
    inputs = iter(['1', 'Новая задача', 'q'])

    # Обеспечение корректного ввода для каждого запроса ввода в функции
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    Commands.update_task_from_input()

    updated_task = setup_task_manager.get_task(task_id)
    assert updated_task.title == "Новая задача"

def test_done_task(setup_task_manager):
    """Тестирование завершения задачи."""
    task_id = setup_task_manager.add_task(tasks[0])

    Commands.done_task()
    updated_task = setup_task_manager.get_task(task_id)

    assert updated_task.status == "Выполнена"
