from commands import Commands as Co
import logging.config
import atexit

logging.config.fileConfig(r'logging\logging.ini')
logger = logging.getLogger()


@atexit.register
def cleanup():
    logger.info("Завершение программы")


def main():
    commands = {
        'add': lambda: (Co.create_task_from_input(), logger.info("команда add выполнена")),
        'del': lambda: (Co.delete_task(), logger.info("команда del выполнена")),
        'list': lambda: (Co.print_tasks(), logger.info("команда list выполнена")),
        'update': lambda: (Co.update_task_from_input(), logger.info("команда update выполнена")),
        'help': lambda: (print(Co.read_file('help_text')), logger.info("команда help выполнена")),
        'done': lambda: (Co.done_task(), logger.info("команда done выполнена")),
        'find': lambda: (Co.search_task(), logger.info("команда find выполнена")),
        'exit': lambda: Co.exit_program(),
        'clear': lambda: (Co.clear(), logger.info("команда clear выполнена")),
        'test': lambda: (Co.test(), logger.info("команда test выполнена")),
    }
    print( '-' * 40, "Добро пожаловать в Task Manager!", '-' * 40, Co.read_file('help_text'), sep='\n')
    while True:
        try:
            action = input(">> ")
            if action in commands:
                commands[action]()
            else:
                logger.warning("Неизвестная команда, попробуйте еще раз.")
                print("Неизвестная команда, попробуйте еще раз.\nhelp - список доступных команд.")
        except Exception as e:
            logger.error("Произошла ошибка: %s", e)
            print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    logger.info("Запуск программы")
    main()
