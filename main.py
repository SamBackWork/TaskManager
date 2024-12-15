from log_dir.setup_logging import *
import atexit
from commands import Commands as Co

logger = logging.getLogger()


# Регистрация функции очистки при завершении программы
@atexit.register
def cleanup():
    logger.info("Завершение программы")


# Обработчик ошибок для неверных команд или исключений
def handle_error(error):
    if isinstance(error, FileNotFoundError):
        logger.error("Файл не найден: %s", error)
        print(f"Ошибка: Файл не найден. Проверьте путь: {error.filename}")
    elif isinstance(error, PermissionError):
        logger.error("Ошибка доступа: %s", error)
        print(f"Ошибка: Отказано в доступе. Проверьте права доступа.")
    elif isinstance(error, KeyError):
        logger.error("Неизвестная команда: %s", error)
        print("Ошибка: Неизвестная команда. Используйте команду 'help' для получения списка доступных команд.")
    else:
        logger.error("Произошла непредвиденная ошибка: %s", error)
        print(f"Произошла непредвиденная ошибка: {error}")


# Основная функция программы
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
                # Ошибка при неверной команде
                logger.warning("Неизвестная команда: %s", action)
                print("Неизвестная команда, попробуйте еще раз.\nhelp - список доступных команд.")
        except FileNotFoundError as e:
            handle_error(e)
        except PermissionError as e:
            handle_error(e)
        except KeyError as e:
            handle_error(e)
        except Exception as e:
            # Ловим все остальные ошибки
            handle_error(e)


if __name__ == "__main__":
    logger.info("Запуск программы")
    try:
        main()
    except Exception as e:
        logger.error(f'Произошла ошибка при запуске программы: {e}')
        print(f'Произошла ошибка: {e}')
