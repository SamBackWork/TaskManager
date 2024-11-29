import sqlite3
from dataclasses import dataclass, field, fields
import sys


@dataclass
class Task:
    task_id: int
    title: str = field(metadata={"title": "Название задачи"})
    description: str = field(metadata={"title": "Описание задачи"})
    category: str = field(metadata={"title": "Категория задачи"})
    due_date: str = field(metadata={"title": "Срок выполнения"})
    priority: str = field(metadata={"title": "Приоритет"})
    status: str = "Не выполнена"


class TaskManager:
    def __init__(self, db_name='tasks.db'):
        self.db_name = db_name
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                due_date TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Не выполнена'
            )
            ''')
            connection.commit()

    def add_task(self, task: Task):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute('''
            INSERT INTO tasks (title, description, category, due_date, priority, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (task.title, task.description, task.category, task.due_date, task.priority, task.status))
            connection.commit()
            task.task_id = cursor.lastrowid
            return task

    def delete_task(self, task_id: int):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            connection.commit()
            print(f"Задача с ID {task_id} удалена")

    def list_tasks(self):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM tasks')
            tasks = cursor.fetchall()
            return [Task(*row) for row in tasks]


def create_task_from_input(task_manager: TaskManager) -> Task:
    task_data = {}
    for field_info in fields(Task):
        if "title" in field_info.metadata:
            field_title = field_info.metadata["title"]
            user_input = input(f"Введите {field_title}: ")
            task_data[field_info.name] = user_input

    task = Task(task_id=0, **task_data)
    return task_manager.add_task(task)


def print_tasks(task_manager: TaskManager):
    tasks = task_manager.list_tasks()
    for task in tasks:  # Перебираем все задачи полученные из базы данных
        for field_info in fields(Task):  # Используем fields для получения заголовков
            field_title = field_info.metadata.get("title", field_info.name)
            field_value = getattr(task, field_info.name)  # Получаем значение поля
            print(f"{field_title}: {field_value}")
        print("-" * 40)  # Для визуального разделения задач


def exit_program():
    sys.exit(0)


# Пример использования:
if __name__ == '__main__':
    task_manager = TaskManager()
    # Добавление новой задачи

    print_tasks(task_manager)
    new_task = create_task_from_input(task_manager)
    print(f"Задача добавлена с ID {new_task.task_id}")

    # Вывод списка всех задач
    tasks = task_manager.list_tasks()
    print("Список всех задач:")
    print_tasks(task_manager)

    # Удаление задачи
    delete_id = int(input("Введите ID задачи для удаления: "))
    task_manager.delete_task(delete_id)
    print(f"Задача с ID {delete_id} удалена")
