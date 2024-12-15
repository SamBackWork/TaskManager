from datetime import datetime
from dataclasses import fields
import sys
from logging import getLogger

from task_manager import TaskManager, Task, tasks

logger = getLogger(__name__)
task_manager = TaskManager()


class InputValidator:
    @staticmethod
    def safe_input(prompt, validation_func=None, error_message="Некорректный ввод", allow_empty=False) -> str | None:
        """Безопасный ввод пользователя с обработкой ошибок."""
        while True:
            user_input = input(prompt)
            if user_input.lower() in ['q', 'й']:
                print("Выход из операции.")
                return None
            if not allow_empty and user_input.strip() == '':
                print("Это поле не может быть пустым.")
                continue
            if validation_func and not validation_func(user_input):
                print(error_message)
                continue
            return user_input

    @staticmethod
    def is_valid_date(date_str) -> bool:
        """Проверка корректности формата даты."""
        try:
            datetime.strptime(date_str, '%d.%m.%Y')
            return True
        except ValueError:
            return False

    @staticmethod
    def del_or_not(choice: bool) -> None:
        if choice:
            confirmation = InputValidator.safe_input(
                "Вы уверены, что хотите продолжить удаление? (да/нет): ",
                validation_func=lambda x: x and str(x).strip().lower() in ("да", "нет"),
                error_message='Нужно написать "Да", если хотите продолжить удаление и "Нет" если не хотите')
            if confirmation != 'да':
                print("Удаление отменено.")
                return False
            return True


class Commands:
    """Класс для работы с командами."""

    @staticmethod
    def making_a_choice(delete=False) -> int | None:
        prompt = ("Выберите 1 чтобы вывести все задачи, 2 чтобы выбрать категорию: ",
                  "Выберите 1 чтобы удалить одну задачу по ID и 2, чтобы удалить категорию задач: ")[delete]
        choice = InputValidator.safe_input(
            prompt,
            validation_func=lambda x: x.isdigit() and int(x) in (1, 2),
            error_message="Выбор должен быть цифрой 1 или 2")
        if choice is None:
            return
        choice = int(choice)
        if choice == 2:
            categories = task_manager.execute_query("SELECT DISTINCT category FROM tasks", one_line=False)
            categories_dict = {i: category[0] for i, category in enumerate(categories, start=1)}
            for index, category in categories_dict.items():
                print(f"Категория: '{category}' нажмите {index} ")
            categories_id = categories_dict.keys()
            tmp = True
            while tmp:
                category_id = InputValidator.safe_input(
                    "Введите ID категории: ",
                    validation_func=lambda x: x.isdigit() and int(x) in categories_id,
                    error_message=f"ID категории должен быть числом c {min(categories_id)} до {max(categories_id)} .",
                )
                if category_id is None:
                    return
                categories_id = task_manager.search_tasks(categories_dict[int(category_id)])
                break
            choice_call = (
                lambda: Commands.print_tasks(categories_id),
                lambda: [task_manager.delete_task(e) for e in categories_id]
            )[delete]
            if InputValidator.del_or_not(delete):
                choice_call()
                return
            choice_call()
        if choice == 1:
            choice_call = (Commands.print_tasks, Commands.delete_task)[delete]
            if InputValidator.del_or_not(delete):
                choice_call()
                return
            choice_call()
            return

    @staticmethod
    def create_task_from_input() -> Task:
        """Создает новую задачу из ввода пользователя."""
        task_data = {}
        for field_info in fields(Task):
            if field_info.name not in ('task_id', 'status'):  # Поля `task_id` и `status` заполняются автоматически
                # Для поля даты используем специальную проверку на формат даты
                if field_info.name == 'due_date':
                    user_input = InputValidator.safe_input(
                        f'Заполните поле "{field_info.metadata["title"]}": ',
                        validation_func=InputValidator.is_valid_date,
                        error_message="Дата должна быть в формате ДД.ММ.ГГГГ!",
                        allow_empty=False)
                else:
                    user_input = InputValidator.safe_input(
                        f'Заполните поле "{field_info.metadata["title"]}": ', allow_empty=False)
                if user_input is None:  # Пользователь выбрал выход
                    return None
                task_data[field_info.name] = user_input
        task = Task(task_id=0, **task_data)
        print("-" * 60, "Создана новая задача!", "-" * 60, sep="\n")
        task_id = task_manager.add_task(task)
        Commands.print_tasks(task_id)

    @staticmethod
    def print_tasks(task_id: int | list | None = None) -> int:
        """Выводит информацию о задачах вместе с полями из метаданных. Возвращает количество задач."""
        tasks = task_manager.get_task(task_id) if task_id else task_manager.get_task()
        row = 9
        row2 = 15
        number_of_taks = len(tasks) if isinstance(tasks, list) else 1
        if isinstance(tasks, Task):
            tasks = [tasks]
        for task in tasks:
            field_iter = iter(fields(Task))
            for field_info in field_iter:
                field_title = field_info.metadata.get("title", field_info.name)
                field_value = getattr(task, field_info.name)
                if len(str(field_value)) > 15:
                    print(f"{field_title:>{row}}: {field_value}")
                    continue
                next_field_info = next(field_iter, None)
                if next_field_info:
                    next_field_title = next_field_info.metadata.get("title", next_field_info.name)
                    next_field_value = getattr(task, next_field_info.name)
                    print(f"{field_title:>{row}}: {field_value:<{row2}}"
                          f"{next_field_title:>{row}}: {next_field_value:<{row2}}")
                else:
                    print(f"{field_title:>{row}}: {field_value:<{row2}}")
            print("-" * 60)
        print(f"Всего задач: {number_of_taks}") if number_of_taks != 1 else None
        return number_of_taks

    @staticmethod
    def exit_program():
        print("Завершение программы")
        sys.exit(0)

    @staticmethod
    def update_task_from_input():
        """Обновляет задачу в базе данных на основе переданных ключевых слов аргументов."""
        task_id_input = InputValidator.safe_input(
            "Введите ID задачи, которую хотите редактировать: ",
            validation_func=str.isdigit,
            error_message="ID задачи должен быть целым числом.",
            allow_empty=False
        )
        if task_id_input is None:
            print("Операция редактирования отменена.")
            return
        task_id = int(task_id_input)
        task = task_manager.get_task(task_id)
        if not task:
            return
        updates = {}
        print("Выберите поле для изменения:")
        fields_dict = {i: field for i, field in enumerate(fields(Task)) if field.name != 'task_id'}
        for index, field_info in fields_dict.items():
            print(f"{index}. {field_info.metadata.get('title', field_info.name)}: ( {getattr(task, field_info.name)} )")
        while True:
            choice = InputValidator.safe_input(
                "Введите номер поля для изменения или нажмите 'q' или 'й': ",
                validation_func=lambda x: x.isdigit() and int(x) in fields_dict,
                error_message=f"Пожалуйста, выберите номер поля"
                              f" от {min(fields_dict.keys())} до {max(fields_dict.keys())}",
                allow_empty=False
            )
            if choice is None:
                return
            choice = int(choice)
            field_info = fields_dict[choice]
            new_value = InputValidator.safe_input(
                f'Введите новое значение для поля "{field_info.metadata.get("title", field_info.name)}": ',
                allow_empty=False
            )
            if new_value is None:
                return
            updates[field_info.name] = new_value
            if updates:
                task_manager.update_task(task_id, **updates)
                print("-" * 60, "Задача обновлена!", "-" * 60, sep="\n")
            else:
                print("-" * 60, "Изменений не внесено!", "-" * 60, sep="\n")
            Commands.print_tasks(task_id)

    @staticmethod
    def done_task() -> None:
        """Обновляет статус задачи в базе данных на 'Выполнена'."""
        task_id_input = InputValidator.safe_input(
            "Введите ID задачи, которую вы хотите выполнить: ",
            validation_func=str.isdigit,
            error_message="ID задачи должен быть целым числом.",
            allow_empty=False
        )
        if task_id_input is None:
            print("Операция выполнения задачи отменена.")
            return
        task_id = int(task_id_input)
        task = task_manager.get_task(task_id)
        if not task:
            print(f"Задача с ID {task_id} не найдена.")
            return
        task_manager.update_task(task_id, status="Выполнена")
        print("-" * 60, "Задача выполнена!", "-" * 60, sep="\n")
        Commands.print_tasks(task_id)

    @staticmethod
    def delete_task() -> None:
        """Удаляет задачу из базы данных по ID."""
        task_id_input = InputValidator.safe_input(
            "Введите ID задачи, которую вы хотите удалить: ",
            validation_func=str.isdigit,
            error_message="ID задачи должен быть целым числом.",
            allow_empty=False
        )
        if task_id_input is None:
            print("Операция удаления отменена.")
            return
        task_id = int(task_id_input)
        if task_manager.delete_task(task_id):
            return
        else:
            print(f"Не удалось найти задачу с ID {task_id}. Удаление не выполнено.")

    @staticmethod
    def input_search_task() -> int | list[int] | None:
        """Предлагает пользователю ввести ключевое слово, категорию и статус для поиска задач."""
        print("Введите ключевые параметры для поиска. Оставьте поле пустым для пропуска.")
        keyword = InputValidator.safe_input("Введите ключевое слово для поиска: ", allow_empty=True)
        if keyword is None:
            return None
        category = InputValidator.safe_input("Введите категорию для поиска: ", allow_empty=True)
        if category is None:
            return None
        status = InputValidator.safe_input("Введите статус для поиска: ", allow_empty=True)
        if status is None:
            return None
        if not keyword and not category and not status:
            print("Вы не ввели ни одного параметра для поиска.")
            return None
        return task_manager.search_tasks(keyword, category, status)

    @staticmethod
    def search_task() -> None | list[int] | int:
        """Поиск задач в базе данных по заданным ключевым словам, категории и статусу."""
        task_id = Commands.input_search_task()
        if task_id is None:
            print("Операция поиска задач отменена.")
            return
        if task_id:  # вывод задач
            Commands.print_tasks(task_id)
            return task_id
        else:
            print("По заданным параметрам задач не найдено.")
            return None

    @staticmethod
    def read_file(file_path):
        """Чтение файла."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def clear():
        task_manager.cleanup_database()
        print("База данных очищена.")

    @staticmethod
    def test():
        [task_manager.add_task(task) for task in tasks]
        print("База данных заполнена тестовыми задачами. list - список всех задач.")


if __name__ == '__main__':
    Commands.making_a_choice()
