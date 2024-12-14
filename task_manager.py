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


def sync_with_search_db(func):  # Синхронизация с базой данных
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        search_result = 'еще не выполнена'
        if not self.is_search_db:  # Проверка, не является ли это экземпляром для базы данных поиска
            search_mgr = TaskManager(db_name="search_tasks.db", is_search_db=True)
            modified_args = [Task(**{field: val.lower() if isinstance(val, str) else val for field, val in
                                     arg.__dict__.items()}) if isinstance(arg, Task) else arg for arg in args]
            modified_kwargs = {k: v.lower() if isinstance(v, str) else v for k, v in kwargs.items()}
            search_result = func(search_mgr, *modified_args, **modified_kwargs)

        result = func(self, *args, **kwargs)  # Вызов оригинальной функции
        return search_result if func.__name__ == "search_tasks" else result  # Возвращаем результат поиска

    return wrapper


class TaskManager:
    """ Класс для управления задачами. """

    def __init__(self, db_name='tasks.db', is_search_db=False):
        self.db_name = db_name
        self.is_search_db = is_search_db  # Флаг для определения, является ли база поисковой
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

    def get_task(self, task_id: int | list[int] | None = None) -> Task | None:
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
    def update_task(self, task_id: int, **kwargs):
        """Обновляет задачу в базе данных на основе переданных ключевых слов аргументов."""
        task = self.get_task(task_id)
        if not task:
            return "Task not found"
        # Формируем части SQL-запроса для обновления и значения параметров
        sql_sets = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(task_id)
        # Выполнение запроса обновления
        self.execute_query(f"UPDATE tasks SET {sql_sets} WHERE id = ?", values)
        return self.get_task(task_id)  # Возвращаем обновленное состояние задачи

    @sync_with_search_db
    def add_task(self, task: Task):
        """Добавляет новую задачу в базу данных и возвращает задачу с присвоенным ID."""
        query = '''INSERT INTO tasks (title, description, category, due_date, priority, status)
                   VALUES (?, ?, ?, ?, ?, ?)'''
        params = (task.title, task.description, task.category, task.due_date, task.priority, task.status)
        task_id = self.execute_query(query, params, commit=True)
        return task_id

    @sync_with_search_db
    def search_tasks(self, keyword=None, category=None, status=None) -> list[int] | str:
        """Поиск задач в поисковой базе данных."""
        if self.db_name == "search_tasks.db":
            query_parts = []  # Список частей запроса
            params = []  # Список параметров
            if keyword:  # Если задано ключевое слово
                keyword_pattern = f'%{keyword.lower()}%'  # Создание паттерна для поиска
                query_parts.append('(title LIKE ? OR description LIKE ? OR category LIKE ? OR status LIKE ?)')
                params.extend([keyword_pattern] * 4)  # Добавление pattern для каждого поля
            if category:  # Если задана категория
                query_parts.append('category = ?')  # Добавление части запроса
                params.append(category.lower())  # Добавление параметра в нижнем регистре
            if status:  # Если задан статус
                query_parts.append('status = ?')  # Добавление части запроса
                params.append(status.lower())  # Добавление параметра в нижнем регистре
            query = 'SELECT id FROM tasks'
            if query_parts:  # Если есть части запроса
                query += ' WHERE ' + ' AND '.join(query_parts)  # Добавление части запроса
            result_rows = self.execute_query(query, params,
                                             one_line=False)  # Вызов метода execute_query для выполнения запроса
            print("-" * 40, f"найдено  задач: {len(result_rows)}", "-" * 40, sep="\n")  # Вывод информации
            res = [row[0] for row in result_rows]
            return res  # Возврат списка ID наеденных задач
        else:
            return "Вы не находитесь в поисковой базе данных"

    @sync_with_search_db
    def delete_task(self, task_id: int) -> None | int:
        """Удаляет задачу из базы данных по-заданному ID."""
        name_query = 'SELECT title FROM tasks WHERE id = ?'  # Получить имя задачи для печати информации
        name = self.execute_query(name_query, (task_id,))
        task_name = name[0] if name else None  # Если задача существует, то получить имя задачи
        delete_query = 'DELETE FROM tasks WHERE id = ?'
        self.execute_query(delete_query, (task_id,), commit=True)  # Выполнить запрос на удаление задачи
        if self.db_name == "tasks.db":
            if task_name:  # Если задача существует
                print(f'Задача "{task_name}" с ID {task_id} удалена')  # Вывести информацию о результате
                return task_id

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

    @sync_with_search_db
    def cleanup_database(self):
        self.execute_query('DELETE FROM tasks', commit=True)  # Удалить все задачи из базы данных


tasks = [
    Task(task_id=6, title="Посетить врача", description="Записаться и посетить терапевта для ежегодного осмотра.",
         category="Здоровье", due_date="2023-11-01", priority="Средний", status="Не выполнена"),
    Task(task_id=7, title="Оплатить счета", description="Оплатить коммунальные счета за текущий месяц.",
         category="Личные дела", due_date="2023-10-15", priority="Высокий", status="Не выполнена"),
    Task(task_id=8, title="Обновить резюме", description="Обновить резюме и подготовиться к поиску новой работы.",
         category="Карьера", due_date="2023-11-10", priority="Средний", status="Не выполнена"),
    Task(task_id=9, title="Посадить цветы", description="Посадить весенние цветы в саду.", category="Дом",
         due_date="2023-11-05", priority="Низкий", status="Не выполнена"),
    Task(task_id=10, title="Организовать встречу", description="Организовать встречу с коллегами по работе.",
         category="Работа", due_date="2023-10-25", priority="Высокий", status="Не выполнена"),
    Task(task_id=11, title="Изучить новый язык", description="Провести 30 минут за изучением испанского языка.",
         category="Образование", due_date="2023-10-30", priority="Средний", status="Не выполнена"),
    Task(task_id=12, title="Проанализировать отчет",
         description="Проанализировать квартальный отчет и подготовить обратную связь.", category="Работа",
         due_date="2023-10-18", priority="Высокий", status="Не выполнена"),
    Task(task_id=13, title="Пройти обучение", description="Завершить онлайн-курс по маркетингу.",
         category="Образование", due_date="2023-11-20", priority="Средний", status="Не выполнена"),
    Task(task_id=14, title="Приготовить ужин", description="Приготовить ужин для семьи.", category="Личные дела",
         due_date="2023-10-14", priority="Низкий", status="Не выполнена"),
    Task(task_id=15, title="Посетить музей", description="Посетить новую выставку в местном музее.", category="Отдых",
         due_date="2023-11-15", priority="Низкий", status="Не выполнена"),
    Task(task_id=16, title="Проверить машину", description="Отвезти машину на техосмотр.", category="Личные дела",
         due_date="2023-11-03", priority="Средний", status="Не выполнена"),
    Task(task_id=17, title="Записаться на конференцию",
         description="Зарегистрироваться на международную конференцию по информационным технологиям.",
         category="Работа", due_date="2023-11-12", priority="Средний", status="Не выполнена"),
    Task(task_id=18, title="Встретиться с друзьями", description="Организовать встречу со старыми друзьями.",
         category="Социальные связи", due_date="2023-11-09", priority="Низкий", status="Не выполнена"),
    Task(task_id=19, title="Подготовиться к зиме",
         description="Закупить зимние товары и подготовить дом к зимнему сезону.", category="Дом",
         due_date="2023-11-20", priority="Высокий", status="Не выполнена"),
    Task(task_id=20, title="Провести аудит",
         description="Провести аудит текущих проектов на предмет соответствия стандартам.", category="Работа",
         due_date="2023-10-31", priority="Высокий", status="Не выполнена"),
    Task(task_id=21, title="Посетить родителей", description="Навестить родителей на выходных.", category="Семья",
         due_date="2023-10-16", priority="Средний", status="Не выполнена"),
    Task(task_id=22, title="Устроить гаражную распродажу",
         description="Организовать гаражную распродажу для избавления от ненужных вещей.", category="Дом",
         due_date="2023-11-18", priority="Низкий", status="Не выполнена"),
    Task(task_id=23, title="Обновить ПО", description="Обновить программное обеспечение на всех офисных компьютерах.",
         category="Работа", due_date="2023-10-22", priority="Высокий", status="Не выполнена"),
    Task(task_id=24, title="Поход в поход", description="Организовать поход в горы с друзьями.", category="Отдых",
         due_date="2023-11-01", priority="Средний", status="Не выполнена"),
    Task(task_id=25, title="Провести опрос",
         description="Разработать и провести опрос среди клиентов для получения отзывов.", category="Работа",
         due_date="2023-11-05", priority="Высокий", status="Не выполнена")
]

if __name__ == '__main__':
    manager = TaskManager()
    print(manager.delete_task(task_id=1000))
