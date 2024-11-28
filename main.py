import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Task:
    task_id: int = field(metadata={"title": "ID задачи"})
    title: str = field(metadata={"title": "Название задачи"})
    description: str = field(metadata={"title": "Описание задачи"})
    category: str = field(metadata={"title": "Категория задачи"})
    due_date: str = field(metadata={"title": "Срок выполнения"})
    priority: str = field(metadata={"title": "Приоритет"})
    status: str = field(metadata={"title": "Статус"}, default="Не выполнена")

    def mark_as_completed(self):
        self.status = "Выполнена"


class TaskManager:
    def __init__(self, filename: str):
        self.filename = filename
        self.tasks: List[Task] = self.load_tasks()

    def load_tasks(self) -> List[Task] | Exception:
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                return [Task(**my_task) for my_task in data]
        except FileNotFoundError as e:
            return e

    def save_tasks(self):
        with open(self.filename, 'w') as file:
            json.dump([task.__dict__ for task in self.tasks], file, ensure_ascii=False, indent=4)

    def add_task(self, title: str, description: str, category: str, due_date: str, priority: str):
        task_id = len(self.tasks) + 1
        new_task = Task(task_id, title, description, category, due_date, priority)
        self.tasks.append(new_task)
        self.save_tasks()

    # Подобные методы для изменения, удаления и поиска задач.


def main():
    instructions = {
        "add": lambda: ,
    }


# Пример использования

if __name__ == "__main__":
    manager = TaskManager('tasks.json')
    manager.add_task("Изучить основы Python", "Прочитать книгу по Python",
                     "Обучение", "2024-11-15", "Высокий")
