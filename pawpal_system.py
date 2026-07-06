"""
PawPal+ system logic layer.

This module holds the backend classes for the PawPal+ pet care assistant.
It is a SKELETON generated from the UML draft (see diagrams/uml_draft.mmd):
class names, attributes, and empty method stubs only. Logic is implemented later.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TaskType(Enum):
    """The kind of care a task represents."""
    FEEDING = "feeding"
    WALK = "walk"
    MEDICATION = "medication"
    APPOINTMENT = "appointment"


class TaskStatus(Enum):
    """Where a task is in its lifecycle."""
    PENDING = "pending"
    COMPLETED = "completed"
    MISSED = "missed"
    OVERDUE = "overdue"


@dataclass
class Task:
    """A single unit of pet care work. This is the object the Scheduler prioritizes."""
    task_id: str
    type: TaskType
    pet: "Pet"
    due_time: datetime
    priority: int = 0
    is_recurring: bool = False
    recurrence_rule: str = ""
    status: TaskStatus = TaskStatus.PENDING
    duration: int = 0  # minutes

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def is_overdue(self, current_time: datetime) -> bool:
        """Return True if the task is past its due time and not completed."""
        pass

    def calculate_priority(self) -> int:
        """Compute and return this task's priority score."""
        pass

    def next_occurrence(self) -> datetime:
        """For a recurring task, return the next due time."""
        pass


@dataclass
class Pet:
    """A single animal being cared for."""
    pet_id: str
    name: str
    species: str
    breed: str = ""
    age: int = 0
    weight: float = 0.0
    medical_notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        pass

    def get_upcoming_tasks(self) -> list[Task]:
        """Return this pet's tasks that are still pending."""
        pass

    def get_medical_summary(self) -> str:
        """Return a short summary of the pet's medical info."""
        pass


@dataclass
class Owner:
    """The app user, who owns one or more pets."""
    owner_id: str
    name: str
    email: str = ""
    phone: str = ""
    pets: list[Pet] = field(default_factory=list)
    notification_preference: str = ""

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        pass

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        pass

    def view_schedule(self, date: datetime) -> list[Task]:
        """Return all tasks across the owner's pets for a given day."""
        pass

    def mark_task_complete(self, task: Task) -> None:
        """Mark one of the owner's tasks as complete."""
        pass

    def update_preferences(self, prefs: str) -> None:
        """Update the owner's notification preferences."""
        pass


class Scheduler:
    """The algorithmic brain: organizes and prioritizes tasks for the day."""

    def __init__(self) -> None:
        self.task_queue: list[Task] = []
        self.current_time: datetime | None = None

    def add_task(self, task: Task) -> None:
        """Insert a task into the priority queue."""
        pass

    def get_next_task(self) -> Task:
        """Return the highest-priority pending task."""
        pass

    def get_daily_plan(self, date: datetime) -> list[Task]:
        """Return an ordered list of tasks for the given day."""
        pass

    def reprioritize(self) -> None:
        """Recompute task priorities (e.g. as tasks become overdue)."""
        pass

    def detect_conflicts(self) -> list[Task]:
        """Return tasks that overlap or clash in time."""
        pass

    def generate_reminders(self) -> None:
        """Produce reminders for upcoming or overdue tasks."""
        pass
