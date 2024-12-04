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
    """Декоратор для синхронизации баз данных."""

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        db_search_name = "search_tasks.db"  # Имя базы данных для поисковых запросов
        func(self, *args, **kwargs)  # Вызов оригинальной функции
        self.db_name = db_search_name  # Переключение на поисковую базу данных
        for arg in args:  # Перебор всех аргументов для приведения к нижнему регистру
            if isinstance(arg, Task):  # Проверка, является ли аргумент экземпляром Task
                for fild, value in arg.__dict__.items():  # Перебор всех атрибутов
                    if isinstance(value, str):  # Проверка, является ли значение строкой
                        setattr(arg, fild, value.lower())  # Приведение к нижнему регистру
        kwargs = {key.lower(): value.lower() if isinstance(value, str) else value for key, value in kwargs.items()}
        func(self, *args, **kwargs)  # Вызов оригинальной функции с новыми аргументами и ключевыми словами
        self.db_name = "tasks.db"  # Переключение обратно на основную базу данных

    return wrapper
