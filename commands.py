import sys
from dataclasses import fields
from datetime import datetime

from task_manager import TaskManager, Task

task_manager = TaskManager()


class Commands:
    """Класс для работы с командами."""

    @staticmethod
    def create_task_from_input() -> Task:
        """Создает новую задачу из ввода пользователя."""
        task_data = {}  # Словарь для хранения данных задачи
        for field_info in fields(Task):  # Получение информации о каждом поле
            if field_info.name not in ('task_id', 'status'):  # task_id и status не требуют ввода
                while True:
                    field_title = field_info.metadata["title"]  # Получение названия поля из метаданных на русском
                    user_input = input(f'Заполните поле "{field_title}": ')  # Ввод значения поля
                    if field_info.name == 'due_date':  # Проверка валидности даты
                        try:
                            datetime.strptime(user_input, '%d.%m.%Y')  # проверка формата даты
                        except ValueError:
                            print("Дата должна быть в формате ДД.ММ.ГГГГ.")
                            continue  # Продолжить запрос ввода
                    if user_input.strip() == '':  # Проверка на пустой ввод. Если введено 'q' или 'й', выйти из функции
                        print("Поле не может быть пустым.")
                        exit_input = input(
                            "Нажмите 'q' или 'й' для выхода из редактирования, любую другую клавишу для продолжения: ")
                        if exit_input.lower() in ['q', 'й']:
                            print("Выход из процесса создания задачи.")
                            return None
                    else:
                        task_data[field_info.name] = user_input  # Добавление значения поля в словарь
                        break
        task = Task(task_id=0, **task_data)  # id=0 чтобы в определении класса Task сохранялась последовательность полей
        print("Создана новая задача!", "-" * 40, sep="\n")
        task_id = task_manager.add_task(task)
        Commands.print_tasks(task_id)

    @staticmethod
    def print_tasks(task_id: int | list | None = None):
        """Выводит информацию о задачах вместе с полями из метаданных."""
        if task_id:
            tasks = task_manager.get_task(task_id)  # Получаем задачу (может вернуть один объект или список)
        else:
            tasks = task_manager.get_task()  # Получаем все задачи

        # Обработка случая с одиночной задачей
        if isinstance(tasks, Task):  # Если tasks — это одиночный объект Task
            tasks = [tasks]  # Преобразуем его в список для унифицированной обработки

        # Итерация по каждой задаче в списке
        for task in tasks:
            field_iter = iter(fields(Task))
            for field_info in field_iter:
                field_title = field_info.metadata.get("title", field_info.name)
                field_value = getattr(task, field_info.name)

                if field_info.name == "description":
                    print(f"{field_title}: {field_value}")
                    continue

                next_field_info = next(field_iter, None)
                if next_field_info:
                    next_field_title = next_field_info.metadata.get("title", next_field_info.name)
                    next_field_value = getattr(task, next_field_info.name)
                    print(f"{field_title}: {field_value}    {next_field_title}: {next_field_value}")
                else:
                    print(f"{field_title}: {field_value}")
            print("-" * 40)

    @staticmethod
    def exit_program():
        print("Завершение программы")
        sys.exit(0)

    @staticmethod
    def update_task_from_input():
        """Обновляет задачу в базе данных на основе переданных ключевых слов аргументов."""
        task_id = int(input("Введите ID задачи, которую хотите редактировать: "))
        task = task_manager.get_task(task_id)  # Получение задачи по ID
        updates = {}
        print("Выберите поле для изменения:")
        fields_dict = {i: field for i, field in enumerate(fields(Task)) if
                       field.name != 'task_id'}  # Исключение поля id из выбора
        for index, field_info in fields_dict.items():
            print(f"{index}. {field_info.metadata.get('title', field_info.name)}: ( {getattr(task, field_info.name)} )")
        while True:
            choice = input("Введите номер поля для изменения или 'q' иди 'й' для выхода: ")
            if choice.lower() in 'qй':
                break
            else:
                try:
                    choice = int(choice)
                except ValueError:
                    print("Неверный выбор, попробуйте снова.")
                    continue
            if int(choice) in fields_dict:
                field_info = fields_dict[int(choice)]
                new_value = input(
                    f'Введите новое значение для поля "{field_info.metadata.get('title', field_info.name)}": ')
                updates[field_info.name] = new_value
            else:
                print("Неверный выбор, попробуйте снова.")
        if updates:
            task_manager.update_task(task_id, **updates)
            print("Задача обновлена!", "-" * 40, sep="\n")
        else:
            print("Изменений не внесено!", "-" * 40, sep="\n")
        Commands.print_tasks(task_id)  # Вывод обновленной задачи

    @staticmethod
    def done_task():
        """Обновляет статус задачи в базе данных на 'Выполнена'."""
        task_id = int(input("Введите ID задачи, которую вы хотите выполнить: "))
        task_manager.update_task(task_id, status="Выполнена")
        Commands.print_tasks(task_id)

    @staticmethod
    def delete_task():
        """Удаляет задачу из базы данных по-заданному ID."""
        task_id = int(input("Введите ID задачи, которую вы хотите удалить: "))
        task_manager.delete_task(task_id)

    @staticmethod
    def input_search_task():
        """Предлагает пользователю ввести ключевое слово, категорию и статус для поиска задач."""
        keyword = input("Введите ключевое слово для поиска: ")
        category = input("Введите категорию для поиска: ")
        status = input("Введите статус для поиска: ")
        if not keyword and not category and not status:
            print("Вы не ввели ни одного параметра для поиска.")
        else:
            return print(task_manager.search_tasks(keyword, category, status))

    @staticmethod
    def search_task():
        """Поиск задач в базе данных по заданным ключевым словам, категории и статусу."""
        Commands.print_tasks(task_id=Commands.input_search_task())

    @staticmethod
    def read_file(file_path):  # Чтение файла
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


if __name__ == '__main__':
    task_manager = TaskManager()
    Commands.print_tasks([1, 2, 3])
