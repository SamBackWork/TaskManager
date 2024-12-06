import functools
import sqlite3
from dataclasses import dataclass, field


def sync_with_search_db(func):
    """Декоратор для синхронизации баз данных."""

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        db_search_name = "search_tasks.db"  # Имя базы данных для поисковых запросов
        result = func(self, *args, **kwargs)  # Вызов оригинальной функции
        self.db_name = db_search_name  # Переключение на поисковую базу данных
        for arg in args:  # Перебор всех аргументов для приведения к нижнему регистру
            if isinstance(arg, Task):  # Проверка, является ли аргумент экземпляром Task
                for fild, value in arg.__dict__.items():  # Перебор всех атрибутов
                    if isinstance(value, str):  # Проверка, является ли значение строкой
                        setattr(arg, fild, value.lower())  # Приведение к нижнему регистру
        kwargs = {key.lower(): value.lower() if isinstance(value, str) else value for key, value in kwargs.items()}
        search_result = func(self, *args, **kwargs)  # Вызов оригинальной функции с новыми аргументами и ключевыми словами
        self.db_name = "tasks.db"  # Переключение обратно на основную базу данных
        return search_result if func.__name__ == "search_tasks" else result
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


class BaseManager:
    def __init__(self, db_name='tasks.db'):
        self.db_name = db_name
        self._create_table()

    def execute_query(self, query, params=(), commit=False, one_line=True):
        """Упрощает выполнение запросов к базе данных."""
        with sqlite3.connect(self.db_name) as connection:  # Подключение к поисковой базе данных
            cursor = connection.cursor()  # Создание курсора
            cursor.execute(query, params)  # Выполнение запроса
            if commit:  # Если нужно выполнить коммит
                connection.commit()  # Выполнение изменений в базе данных
                task_id = cursor.lastrowid
                return task_id
            else:
                return cursor.fetchone() if one_line else cursor.fetchall()  # Возврат результата

    def get_task(self, task_id=None):
        """Получает одну или несколько задач из базы данных по заданным ID или все задачи, если ID не указаны."""
        if task_id is None:  # Возвращаем все задачи.
            tasks = self.execute_query('SELECT * FROM tasks', one_line=False)
            return [Task(*row) for row in tasks]
        elif isinstance(task_id, list):  # Возвращаем задачи для списка ID.
            result_tasks = []
            for e in task_id:
                task_row = self.execute_query('SELECT * FROM tasks WHERE id = ?', (e,))
                if task_row:
                    result_tasks.append(Task(*task_row))
            return result_tasks
        else:  # Возвращаем задачу для одного ID.
            task_row = self.execute_query('SELECT * FROM tasks WHERE id = ?', (task_id,))
            if not task_row:
                print(f'Задача с ID {task_id} не найдена')
                return None
            return Task(*task_row)

    @sync_with_search_db
    def delete_task(self, task_id: int):
        """Удаляет задачу из базы данных по-заданному ID."""
        name_query = 'SELECT title FROM tasks WHERE id = ?'  # Получить имя задачи для печати информации
        name = self.execute_query(name_query, (task_id,))
        task_name = name[0] if name else 'Неизвестная задача'
        delete_query = 'DELETE FROM tasks WHERE id = ?'
        self.execute_query(delete_query, (task_id,), commit=True)  # Выполнить запрос на удаление задачи
        if self.db_name == "tasks.db":
            print(f'Задача "{task_name}" с ID {task_id} удалена')  # Вывести информацию о результате

    @sync_with_search_db
    def _create_table(self):
        """Создает таблицу задач, если она еще не существует."""
        query = '''CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        category TEXT NOT NULL,
                        due_date TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'Не выполнена'
                    )'''
        self.execute_query(query, commit=True)
