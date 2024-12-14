import atexit
import logging.config

from commands import Commands as Co

logging.config.fileConfig(r'logging\logging.ini')
logger = logging.getLogger()


@atexit.register
def cleanup():
    logger.info("Завершение программы")


def main():
    commands = {
        'add': lambda: (Co.create_task_from_input(), logger.info("Команда add выполнена")),
        'del': lambda: (Co.delete_task(), logger.info("Команда del выполнена")),
        'list': lambda: (Co.print_tasks(), logger.info("Команда list выполнена")),
        'update': lambda: (Co.update_task_from_input(), logger.info("Команда update выполнена")),
        'help': lambda: (print(Co.read_file('help_text')), logger.info("Команда help выполнена")),
        'done': lambda: (Co.done_task(), logger.info("Команда done выполнена")),
        'find': lambda: (Co.search_task(), logger.info("Команда find выполнена")),
        'exit': lambda: Co.exit_program(),
        'clear': lambda: (Co.clear(), logger.info("Команда clear выполнена")),
        'test': lambda: (Co.test(), logger.info("Команда test выполнена")),
    }
    print('-' * 60, f"{' ' * 12}Добро пожаловать в Task Manager!", '-' * 60, Co.read_file('help_text'), sep='\n')
    while True:
        try:
            action = input(">> ")
            if action in commands:
                commands[action]()
            else:
                logger.warning("Неизвестная команда '%s', попробуйте еще раз.", action)
                print("Неизвестная команда, попробуйте еще раз.\nhelp - список доступных команд.")
        except Exception as e:
            logger.error("Произошла ошибка: %s", e)
            print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    logger.info("Запуск программы")
    try:
        main()
    except Exception as e:
        logger.error(f'Произошла ошибка: {e}')
