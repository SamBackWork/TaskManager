import sqlite3
from dataclasses import dataclass, field, fields
import sys


@dataclass
class Task:
    task_id: int = field(metadata={"title": "ID задачи"})
    title: str = field(metadata={"title": "Название задачи"})
    description: str = field(metadata={"title": "Описание задачи"})
    category: str = field(metadata={"title": "Категория задачи"})
    due_date: str = field(metadata={"title": "Срок выполнения"})
    priority: str = field(metadata={"title": "Приоритет"})
    status: str = field(metadata={"title": "Статус"}, default="Не выполнена")


class TaskManager:
    def __init__(self, db_name='tasks.db'):
        self.db_name = db_name
        self._create_table()

    def update_task(self, task_id: int, **kwargs):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            query_parts = []
            values = []
            for key, value in kwargs.items():
                if key in Task.__annotations__ and key != 'task_id':  # Ensure the field is in Task and not the id field
                    query_parts.append(f"{key} = ?")
                    values.append(value)
            if not query_parts:
                raise ValueError("Нет полей для обновления")
            query = f"UPDATE tasks SET {', '.join(query_parts)} WHERE id = ?"
            values.append(task_id)
            cursor.execute(query, values)
            connection.commit()
            print(f"Задача с ID {task_id} обновлена.")

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
            cursor.execute('SELECT title FROM tasks WHERE id = ?', (task_id,))
            name = cursor.fetchone()[0]
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            connection.commit()
            print(f'Задача "{name}" с ID {task_id} удалена')

    def list_tasks(self):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM tasks')
            tasks = cursor.fetchall()
            return [Task(*row) for row in tasks]


def create_task_from_input(task_manager: TaskManager) -> Task:
    task_data = {}
    for field_info in fields(Task):
        if field_info.name not in ('task_id', 'status'):
            field_title = field_info.metadata["title"]
            user_input = input(f"Введите {field_title}: ")
            task_data[field_info.name] = user_input

    task = Task(task_id=0, **task_data)
    return task_manager.add_task(task)


def print_tasks(task_manager: TaskManager):
    tasks = task_manager.list_tasks()
    for task in tasks:  # Перебираем все задачи полученные из базы данных
        for field_info in fields(Task):
            field_title = field_info.metadata.get("title", field_info.name)
            field_value = getattr(task, field_info.name)  # Получаем значение поля
            print(f"{field_title}: {field_value}")
        print("-" * 40)  # Для визуального разделения задач


def exit_program():
    print("Завершение программы")
    sys.exit(0)


def update_task_from_input(task_manager: TaskManager):
    task_id = int(input("Введите ID задачи, которую хотите редактировать: "))
    updates = {}
    for field_info in fields(Task):
        if field_info.name != 'task_id':  # Skip the task_id field
            if input(f"Вы хотите изменить {field_info.metadata['title']}? (y/n) ").lower() == 'y':
                new_value = input(f"Введите новое значение для {field_info.metadata['title']}: ")
                updates[field_info.name] = new_value
    if updates:
        task_manager.update_task(task_id, **updates)
    else:
        print("Изменения не внесены.")


def read_file(file_path):  # Чтение файла
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
