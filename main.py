from commands import Commands as co, read_file
from utils import TaskManager


def main():
    my_task_manager = TaskManager()
    commands = {
        'add': lambda: co.create_task_from_input(my_task_manager),
        'del': lambda: co.delete_task(my_task_manager),
        'list': lambda: co.print_tasks(my_task_manager),
        'update': lambda: co.update_task_from_input(my_task_manager),
        'help': lambda: print(read_file('help_text')),
        'done': lambda: co.done_task(my_task_manager),
        'find': lambda: co.search_task(my_task_manager),
        'exit': lambda: co.exit_program(),
    }
    print(read_file('help_text'))
    while True:
        try:
            action = input(">> ")
            if action in commands:
                commands[action]()
            else:
                print("Неизвестная команда, попробуйте еще раз.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
