from dataclasses import dataclass, field
from datatime import date, timedelta
from typing import Optional


@dataclass
class Task:
    description: str
    time: str
    frequency: str
    pet_name: str
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def mark_complete(self):
        pass

    def __str__(self):
        pass

class Pet:
    def __init__(self, name: str, species: str, age: int):
        self.name = name
        self.species = species
        self.age = age
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        pass

    def get_tasks(self) -> list[Task]:
        pass

    def __str__(self):
        pass

class Owner:
    def __init__(self, name: str):
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet):
        pass

    def remove_pet(self, pet_name: str):
        pass

    def get_all_tasks(self) -> list[Task]:
        pass

    def get_pet(self, name: str) -> Optional[Pet]:
        pass

class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def sort_by_time(self) -> list[Task]:
        pass

    def filter_by_status(self, completed: bool) -> list[Task]:
        pass

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        pass

    def detect_conflicts(self) -> list[str]:
        pass

    def mark_task_complete(self, task: Task):
        pass

    def todays_schedule(self) -> list[Task]:
        pass