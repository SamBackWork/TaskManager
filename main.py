from commands import Commands as Co


def main():
    commands = {
        'add': lambda: Co.create_task_from_input(),
        'del': lambda: Co.delete_task(),
        'list': lambda: Co.print_tasks(),
        'update': lambda: Co.update_task_from_input(),
        'help': lambda: print(Co.read_file('help_text')),
        'done': lambda: Co.done_task(),
        'find': lambda: Co.search_task(),
        'exit': lambda: Co.exit_program(),
    }
    print(Co.read_file('help_text'))
    while True:
        try:
            action = input(">> ")
            if action in commands:
                commands[action]()
            else:
                print("Неизвестная команда, попробуйте еще раз.\nhelp - список доступных команд.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
