import json
from dataclasses import dataclass, field, fields
from typing import List, Dict, Optional, ClassVar


@dataclass
class Task:
    title: str = field(metadata={"title": "Название задачи"})
    description: str = field(metadata={"title": "Описание задачи"})
    category: str = field(metadata={"title": "Категория задачи"})
    due_date: str = field(metadata={"title": "Срок выполнения"})
    priority: str = field(metadata={"title": "Приоритет"})
    status: str = "Не выполнена"
    task_id: int = 0

    __last_id: ClassVar[int] = 0

    def __post_init__(self):
        self.task_id = Task.__last_id + 1
        Task.__last_id = self.task_id

    def mark_as_completed(self):
        self.status = "Выполнена"


@dataclass
class TaskManager:
    filename: str = "tasks.json"
    tasks: List[Task] = field(default_factory=list)

    def load_tasks(self) -> List[Task]:
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                return [Task(**task_data) for task_data in data]  # Convert dicts back to Task instances
        except FileNotFoundError:
            return []  # Return an empty list

    @staticmethod
    def create_task_from_input():
        task_data = {}

        for field_info in fields(Task):
            if "title" in field_info.metadata:
                field_title = field_info.metadata.get("title", field_info.name)
                user_input = input(f"{field_title}: ")
                task_data[field_info.name] = user_input

        task = Task(**task_data)
        return task

    def add_task(self):
        new_task = self.create_task_from_input()
        self.tasks.append(new_task)
        self.save_tasks()

    def save_tasks(self):
        with open(self.filename, 'w') as file:
            json.dump([task.__dict__ for task in self.tasks], file, ensure_ascii=True, indent=4)


task_manager = TaskManager()
task_manager.add_task()

for task in task_manager.tasks:  # Перебираем all задачи в task_manager для удобного вывода
    print("Информация о задаче:")
    for field_info in fields(Task):
        # Получаем заголовок поля из metadata или используем name поля как заголовок
        field_title = field_info.metadata.get("title", field_info.name)
        field_value = getattr(task, field_info.name)  # Получаем значение поля
        print(f"{field_title}: {field_value}")
    print("-" * 40)  # Для визуального разделения задач
