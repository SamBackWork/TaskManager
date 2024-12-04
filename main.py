from commands import Commands as co, read_file


def main():
    commands = {
        'add': lambda: co.create_task_from_input(),
        'del': lambda: co.delete_task(),
        'list': lambda: co.print_tasks(),
        'update': lambda: co.update_task_from_input(),
        'help': lambda: print(read_file('help_text')),
        'done': lambda: co.done_task(),
        'find': lambda: co.search_task(),
        'exit': lambda: co.exit_program(),
        'res': lambda: co.restart_program()
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
