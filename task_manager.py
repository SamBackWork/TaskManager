from base_utils import sync_with_search_db, Task, BaseManager


class TaskManager(BaseManager):
    """ Класс для управления задачами. """

    def __init__(self):
        super().__init__()

    @sync_with_search_db
    def update_task(self, task_id: int, **kwargs):
        """Обновляет задачу в базе данных на основе переданных ключевых слов аргументов."""
        task = self.get_task(task_id)
        if not task:
            return None
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
    def search_tasks(self, keyword=None, category=None, status=None):
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
            print(f" Найдено {len(result_rows)} задач: ")  # Вывод количества найденных задач
            res = [row[0] for row in result_rows]
            return res  # Возврат списка ID наеденных задач
        else:
            return "Вы не находитесь в поисковой базе данных"


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
    for task in tasks:
        task_manager.add_task(task)