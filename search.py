import functools
import sqlite3
from dataclasses import dataclass, field


@dataclass
class Task:
    task_id: int = field(metadata={"title": "ID задачи"})
    title: str = field(metadata={"title": "Название задачи"})
    description: str = field(metadata={"title": "Описание задачи"})
    category: str = field(metadata={"title": "Категория задачи"})
    due_date: str = field(metadata={"title": "Срок выполнения"})
    priority: str = field(metadata={"title": "Приоритет"})
    status: str = field(metadata={"title": "Статус"}, default="Не выполнена")


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
        kwargs = {key.lower(): value.lower() if isinstance(value, str) else value for key, value in kwargs.items()}
        func(self, *args, **kwargs)
        self.db_name = "tasks.db"

    return wrapper


class SearchMixin:
    def __init__(self, db_search_name='search_tasks.db'):
        self.db_search_name = db_search_name

    def search_tasks(self, keyword=None, category=None, status=None):
        with sqlite3.connect(self.db_search_name) as connection:
            cursor = connection.cursor()
            query_parts = []
            params = []

            if keyword:
                keyword_pattern = f'%{keyword.lower()}%'
                query_parts.append(f'(title LIKE ? OR description LIKE ? OR category LIKE ? OR status LIKE ?)')
                params.extend([keyword_pattern] * 4)  # Добавление pattern для каждого поля

            if category:
                query_parts.append('category = ?')
                params.append(category.lower())

            if status:
                query_parts.append('status = ?')
                params.append(status.lower())

            query = 'SELECT id FROM tasks'
            if query_parts:
                query += ' WHERE ' + ' AND '.join(query_parts)

            cursor.execute(query, params)
            result_rows = cursor.fetchall()
            print(f" Найдено {len(result_rows)} задач: ")
            return [row[0] for row in result_rows]


if __name__ == '__main__':
    my_search = SearchMixin()
    print(my_search.search_tasks(status='Выполнена'))
