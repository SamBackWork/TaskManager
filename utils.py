import sqlite3
from dataclasses import dataclass, field
import functools


def sync_with_search_db(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        db_search_name = "search_tasks.db"
        func(self, *args, **kwargs)
        self.db_name = db_search_name
        for arg in args:
            if isinstance(arg, Task):
                for fild, value in arg.__dict__.items():
                    if isinstance(value, str):
                        setattr(arg, fild, value.lower())
        func(self, *args, **kwargs)
        self.db_name = "tasks.db"

    return wrapper


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
    backup_instance = None  # Статический атрибут для резервного менеджера

    def __init__(self, db_name='tasks.db'):
        self.db_name = db_name
        self._create_table()

    @sync_with_search_db
    def _create_table(self):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                due_date TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Не выполнена'
            )''')
            connection.commit()

    @sync_with_search_db
    def add_task(self, task: Task):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute('''INSERT INTO tasks (title, description, category, due_date, priority, status)
                              VALUES (?, ?, ?, ?, ?, ?)''',
                           (task.title, task.description, task.category, task.due_date, task.priority, task.status))
            connection.commit()
            task.task_id = cursor.lastrowid
            return task

    @sync_with_search_db
    def delete_task(self, task_id: int):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT title FROM tasks WHERE id = ?', (task_id,))
            name = cursor.fetchone()[0]
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            connection.commit()
            print(f'Задача "{name}" с ID {task_id} удалена')

    @sync_with_search_db
    def list_tasks(self):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM tasks')
            tasks = cursor.fetchall()
            return [Task(*row) for row in tasks]

    @sync_with_search_db
    def search_tasks(self, keyword=None, category=None, status=None):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()

            # Начальное условие
            query_parts = []
            params = []

            # Общий поиск по всем полям
            if keyword:
                query_parts.append(
                    '((title) LIKE (?) OR (description) LIKE (?) OR (category) LIKE (?) OR (status) LIKE (?))')
                keyword_pattern = f'%{keyword}%'
                params.extend([keyword_pattern] * 4)  # Добавляем 4 раза для всех полей

            # Фильтр по категории
            if category:
                query_parts.append('(category) = (?)')
                params.append(category)

            # Фильтр по статусу
            if status:
                query_parts.append('(status) = (?)')
                params.append(status)

            # Соединяем запрос
            query = 'SELECT * FROM tasks'  # Начинаем с выбора из таблицы
            if query_parts:
                query += ' WHERE ' + ' AND '.join(query_parts)  # Если есть условия, добавляем WHERE

            cursor.execute(query, params)
            result_rows = cursor.fetchall()

            return [Task(*row) for row in result_rows]


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
if __name__ == '__main__':
    task_manager = TaskManager()
    task_manager.initialize_backup()  # Инициализируем резервный экземпляр
    from commands import print_tasks

    for task in tasks:
        task_manager.add_task(task)

