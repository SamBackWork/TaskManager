import sys
from dataclasses import fields
from utils import TaskManager, Task


# TODO: реализовать возможность ввоода команд сразу с ID задачи
# TODO: написать коментарии к каждой строке в каждой функции

def create_task_from_input(task_manager: TaskManager) -> Task:
    task_data = {}
    for field_info in fields(Task):
        if field_info.name not in ('task_id', 'status'):
            field_title = field_info.metadata["title"]
            user_input = input(f"Введите {field_title}: ")
            task_data[field_info.name] = user_input

    task = Task(task_id=0, **task_data)
    return task_manager.add_task(task)


def print_tasks(task_manager: TaskManager | list[Task]):
    try:
        tasks = task_manager.list_tasks()
    except:
        tasks = task_manager
    for task in tasks:  # Перебираем все задачи полученные из базы данных
        for field_info in fields(Task):
            field_title = field_info.metadata.get("title", field_info.name)
            field_value = getattr(task, field_info.name)  # Получаем значение поля
            print(f"{field_title}: {field_value}")
        print("-" * 40)  # Для визуального разделения задач


def exit_program():
    print("Завершение программы")
    sys.exit(0)


# TODO: реализовать возможность выбора изменения задач без перебора полей, а выбором цыфры меню
# TODO: когда будет вывод меню редактирования, нужно выводить имя задачи и ID
def update_task_from_input(task_manager: TaskManager):
    task_id = int(input("Введите ID задачи, которую хотите редактировать: "))
    updates = {}
    for field_info in fields(Task):
        if field_info.name != 'task_id':  # Skip the task_id field
            if input(f"Вы хотите изменить {field_info.metadata['title']}? (y/n) ").lower() == 'y':
                new_value = input(f"Введите новое значение для {field_info.metadata['title']}: ")
                updates[field_info.name] = new_value
    if updates:
        task_manager.update_task(task_id, **updates)
    else:
        print("Изменения не внесены.")


def done_task(task_manager: TaskManager):
    task_id = int(input("Введите ID задачи, которую вы хотите выполнить: "))
    task_manager.update_task(task_id, status="Выполнена")


def delete_task(task_manager: TaskManager):
    task_id = int(input("Введите ID задачи, которую вы хотите удалить: "))
    task_manager.delete_task(task_id)


def read_file(file_path):  # Чтение файла
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
