import sqlite3
from search import sync_with_search_db, Task, SearchMixin


class TaskManager(SearchMixin):
    def __init__(self, db_name='tasks.db'):
        super().__init__()
        self.db_name = db_name
        self._create_table()

    @sync_with_search_db
    def update_task(self, task_id: int, **kwargs):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            task = Task(*cursor.fetchone())
            for field, value in kwargs.items():
                setattr(task, field, value)
            cursor.execute(
                'UPDATE tasks SET title = ?, description = ?, category = ?, due_date = ?, priority = ?, status = ? WHERE id = ?',
                (task.title, task.description, task.category, task.due_date, task.priority, task.status, task_id))
            connection.commit()
            return task

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

    def list_tasks(self, task_id: int | list[int] | None = None) -> list[Task] | list:
        """
        Эта функция возвращает полный список задач из базы данных если не указан task_id
        Если task_id указан, то возвращает список задач по id
        :param task_id: id задачи или список id задач
        :return: список задач или
        """
        with sqlite3.connect(self.db_name) as connection:  # Используем контекст менеджера
            result_list_tasks = []  # Создаем пустой список
            if task_id is None:  # Если task_id не указан
                cursor = connection.cursor()  # Создаем курсор базы данных для выполнения запроса
                cursor.execute('SELECT * FROM tasks')  # Выполняем запрос
                tasks = cursor.fetchall()  # Получаем все строки результата запроса
                return [Task(*row) for row in tasks]  # Возвращаем список задач
            if isinstance(task_id, list):  # Если task_id указан
                for id in task_id:  # Проходим по каждому id
                    cursor = connection.cursor()  # Создаем курсор базы данных для выполнения запроса
                    cursor.execute('SELECT * FROM tasks WHERE id = ?', (id,))  # Выполняем запрос
                    row = cursor.fetchone()  # Получаем одну строку результата запроса и сохраняем в переменную
                    if row:  # Если строка не пустая
                        result_list_tasks.append(Task(*row))  # Добавляем строку в список
                return result_list_tasks  # Возвращаем список
            else:
                cursor = connection.cursor()  # Создаем курсор базы данных для выполнения запроса
                cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))  # Выполняем запрос
                tasks = cursor.fetchall()  # Получаем все строки результата запроса
                return [Task(*row) for row in tasks]  # Возвращаем список задач


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
    task_manager = TaskManager()
    # for task in tasks:
    #     task_manager.add_task(task)
    # print(task_manager.search_tasks(keyword='Работа', category=None, status=None))
