import sqlite3
from dataclasses import dataclass, field
import functools


def sync_with_backup_db(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Вызов оригинальной функции
        result = func(self, *args, **kwargs)

        # Подключение к резервной базе данных и дублирование изменений
        backup_db_name = 'backup_tasks.db'
        with sqlite3.connect(backup_db_name) as backup_connection:
            backup_cursor = backup_connection.cursor()

            # Предполагаем, что структура таблицы точно такая же
            if func.__name__ == 'add_task':
                task = args[0]
                backup_cursor.execute('''
                    INSERT INTO tasks (title, description, category, due_date, priority, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (task.title, task.description, task.category, task.due_date, task.priority, task.status))
            elif func.__name__ == 'delete_task':
                task_id = args[0]
                backup_cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            elif func.__name__ == 'update_task':
                task_id = args[0]
                values = args[1:]
                update_values = ', '.join([f"{k} = '{v}'" for k, v in kwargs.items() if k != 'task_id'])
                backup_cursor.execute(f'UPDATE tasks SET {update_values} WHERE id = ?', (task_id,))

            backup_connection.commit()

        return result

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
    def __init__(self, db_name='tasks.db'):
        self.db_name = db_name
        self._create_table()

    def update_task(self, task_id: int, **kwargs):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT title FROM tasks WHERE id = ?', (task_id,))
            name = cursor.fetchone()[0]
            query_parts = []
            values = []
            for key, value in kwargs.items():
                if key in Task.__annotations__ and key != 'task_id':
                    query_parts.append(f"{key} = ?")
                    values.append(value)
            if not query_parts:
                raise ValueError("Нет полей для обновления")
            query = f"UPDATE tasks SET {', '.join(query_parts)} WHERE id = ?"
            values.append(task_id)
            cursor.execute(query, values)
            connection.commit()
            print(f'Задача "{name}" с ID {task_id} обновлена.')

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


if __name__ == '__main__':
    task_manager = TaskManager()
    from commands import print_tasks

    search_tasks = task_manager.search_tasks(status='выполнена')
    print(f"Найдено задач: {len(search_tasks)}")
    print_tasks(search_tasks)
