from utils import TaskManager
from commands import *


def main():
    my_task_manager = TaskManager()
    instructions = {
        'add': lambda: create_task_from_input(my_task_manager),
        'del': lambda: delete_task(my_task_manager),
        'list': lambda: print_tasks(my_task_manager),
        'update': lambda: update_task_from_input(my_task_manager),
        'help': lambda: print(read_file('help_text')),
        'done': lambda: done_task(my_task_manager),
        'exit': lambda: exit_program(),
    }
    print(read_file('help_text'))
    while True:
        try:
            action = input(">> ")
            if action in instructions:
                instructions[action]()
            else:
                print("Неизвестная команда, попробуйте еще раз.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
