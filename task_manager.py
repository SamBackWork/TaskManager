from base_utils import sync_with_search_db, Task, BaseManager


class TaskManager(BaseManager):
    """ Класс для управления задачами. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

