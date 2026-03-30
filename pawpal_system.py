from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


@dataclass
class Task:
    """Represents a single pet care activity."""

    description: str
    time: str
    frequency: str
    pet_name: str
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task complete and return the next recurrence if applicable."""
        self.completed = True
        if self.frequency == "daily":
            return Task(self.description, self.time, self.frequency, self.pet_name, self.due_date + timedelta(days=1))
        elif self.frequency == "weekly":
            return Task(self.description, self.time, self.frequency, self.pet_name, self.due_date + timedelta(weeks=1))
        return None

    def __str__(self) -> str:
        status = "done" if self.completed else "pending"
        return f"[{self.time}] {self.description} ({self.pet_name}) | {self.frequency} | {status}"


class Pet:
    """Represents a pet and its list of care tasks."""

    def __init__(self, name: str, species: str, age: int):
        self.name = name
        self.species = species
        self.age = age
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return self.tasks

    def __str__(self) -> str:
        return f"{self.name} ({self.species}, age {self.age})"


class Owner:
    """Represents a pet owner who manages one or more pets."""

    def __init__(self, name: str):
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across all pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks

    def get_pet(self, name: str) -> Optional[Pet]:
        """Return a pet by name, case-insensitive."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    def __str__(self) -> str:
        return f"{self.name} | pets: {[p.name for p in self.pets]}"


class Scheduler:
    """Organizes, filters, and validates tasks for an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        """Retrieve all tasks from the owner."""
        return self.owner.get_all_tasks()

    def sort_by_time(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks sorted chronologically by HH:MM time string."""
        tasks = tasks if tasks is not None else self.get_all_tasks()
        return sorted(tasks, key=lambda t: t.time)

    def filter_by_status(self, completed: bool, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks filtered by completion status."""
        tasks = tasks if tasks is not None else self.get_all_tasks()
        return [t for t in tasks if t.completed == completed]

    def filter_by_pet(self, pet_name: str, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks for a specific pet."""
        tasks = tasks if tasks is not None else self.get_all_tasks()
        return [t for t in tasks if t.pet_name.lower() == pet_name.lower()]

    def filter_by_date(self, target_date: date, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks scheduled for a specific date."""
        tasks = tasks if tasks is not None else self.get_all_tasks()
        return [t for t in tasks if t.due_date == target_date]

    def detect_conflicts(self, tasks: Optional[list[Task]] = None) -> list[str]:
        """Return warnings for tasks sharing the same time and date."""
        tasks = tasks if tasks is not None else self.get_all_tasks()
        seen: dict[tuple, list[Task]] = {}
        for task in tasks:
            key = (task.time, task.due_date)
            seen.setdefault(key, []).append(task)
        warnings = []
        for (time, due_date), group in seen.items():
            if len(group) > 1:
                names = ", ".join(t.description for t in group)
                warnings.append(f"Conflict at {time} on {due_date}: [{names}]")
        return warnings

    def mark_task_complete(self, task: Task) -> None:
        """Mark a task complete and schedule the next recurrence if needed."""
        next_task = task.mark_complete()
        if next_task:
            pet = self.owner.get_pet(task.pet_name)
            if pet:
                pet.add_task(next_task)

    def todays_schedule(self) -> list[Task]:
        """Return today's tasks sorted by time."""
        return self.sort_by_time(self.filter_by_date(date.today()))