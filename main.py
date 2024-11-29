from utils import *


def main():
    my_task = TaskManager()
    instructions = {
        'add': lambda: create_task_from_input(my_task),
        'del': lambda: my_task.delete_task(int(input("Введите ID задачи для удаления: "))),
        'list': lambda: print_tasks(my_task),
        'exit': lambda: exit_program(),
    }
    while True:
        try:
            text = input(">>")
            if text in instructions:
                instructions[text]()  # Вызов функции из словаря
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()  # Запуск программы