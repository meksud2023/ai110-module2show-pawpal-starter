"""
PawPal+ system logic layer.

This module holds the backend classes for the PawPal+ pet care assistant.
Design follows the UML draft (see diagrams/uml_draft.mmd):
  Owner owns many Pets, a Pet has many Tasks, and the Scheduler manages Tasks.

The classes here are the system's "brain" and are built/verified from the CLI
(see main.py) before being connected to the Streamlit UI.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
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


# Base priority weight per task type. Higher = more important.
# Medication is most critical, a walk is least. The Scheduler uses these
# scores (bumped for overdue tasks) to decide ordering.
PRIORITY_WEIGHTS = {
    TaskType.MEDICATION: 100,
    TaskType.APPOINTMENT: 80,
    TaskType.FEEDING: 60,
    TaskType.WALK: 40,
}


@dataclass
class Task:
    """A single unit of pet care work. This is the object the Scheduler prioritizes."""
    task_id: str
    type: TaskType
    pet: "Pet"
    due_time: datetime
    priority: int = 0
    is_recurring: bool = False
    recurrence_rule: str = ""  # e.g. "daily", "weekly", "hourly"
    status: TaskStatus = TaskStatus.PENDING
    duration: int = 0  # minutes

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.status = TaskStatus.COMPLETED

    def is_overdue(self, current_time: datetime) -> bool:
        """Return True if the task is past its due time and not yet completed."""
        if self.status == TaskStatus.COMPLETED:
            return False
        return current_time > self.due_time

    def calculate_priority(self) -> int:
        """Compute this task's priority score from its type, store it, and return it."""
        self.priority = PRIORITY_WEIGHTS.get(self.type, 0)
        return self.priority

    def next_occurrence(self) -> datetime:
        """For a recurring task, return the next due time based on its recurrence rule."""
        if not self.is_recurring:
            return self.due_time
        rule = self.recurrence_rule.lower().strip()
        deltas = {
            "hourly": timedelta(hours=1),
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
        }
        return self.due_time + deltas.get(rule, timedelta())


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
        """Attach a care task to this pet (no duplicates)."""
        if task not in self.tasks:
            self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet, if present."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_upcoming_tasks(self) -> list[Task]:
        """Return this pet's tasks that are not yet completed."""
        return [t for t in self.tasks if t.status != TaskStatus.COMPLETED]

    def get_medical_summary(self) -> str:
        """Return a short human-readable summary of the pet's medical info."""
        notes = self.medical_notes if self.medical_notes else "No medical notes on file"
        return f"{self.name} ({self.species}, {self.age}y, {self.weight}kg): {notes}"


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
        """Register a pet under this owner (no duplicates)."""
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner, if present."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_all_tasks(self) -> list[Task]:
        """Collect and return every task across all of this owner's pets."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def view_schedule(self, date: datetime) -> list[Task]:
        """Return all tasks across the owner's pets that fall on the given day."""
        return [t for t in self.get_all_tasks() if t.due_time.date() == date.date()]

    def mark_task_complete(self, task: Task) -> None:
        """Mark one of the owner's tasks as complete."""
        task.mark_complete()

    def update_preferences(self, prefs: str) -> None:
        """Update the owner's notification preference."""
        self.notification_preference = prefs


class Scheduler:
    """The algorithmic brain: organizes and prioritizes tasks for the day."""

    def __init__(self, current_time: datetime | None = None) -> None:
        """Create a scheduler with an empty task queue and a reference 'now'."""
        self.task_queue: list[Task] = []
        self.current_time: datetime = current_time or datetime.now()

    def add_task(self, task: Task) -> None:
        """Insert a single task into the queue."""
        self.task_queue.append(task)

    def add_tasks(self, tasks: list[Task]) -> None:
        """Load many tasks at once, e.g. all tasks across an owner's pets."""
        self.task_queue.extend(tasks)

    def _sort_key(self, task: Task):
        """Ordering key: overdue tasks first, then higher priority, then earlier due time."""
        overdue = task.is_overdue(self.current_time)
        # not-overdue sorts after overdue (False < True, so negate); higher priority first.
        return (not overdue, -task.calculate_priority(), task.due_time)

    def get_next_task(self) -> Task | None:
        """Return the single highest-priority pending task, or None if there are none."""
        pending = [t for t in self.task_queue if t.status == TaskStatus.PENDING]
        if not pending:
            return None
        return sorted(pending, key=self._sort_key)[0]

    def get_daily_plan(self, date: datetime) -> list[Task]:
        """Return this day's pending tasks, ordered by priority and urgency."""
        todays = [
            t for t in self.task_queue
            if t.due_time.date() == date.date() and t.status == TaskStatus.PENDING
        ]
        return sorted(todays, key=self._sort_key)

    def reprioritize(self) -> None:
        """Recompute every task's priority and re-order the queue in place."""
        for task in self.task_queue:
            task.calculate_priority()
        self.task_queue.sort(key=self._sort_key)

    def detect_conflicts(self) -> list[Task]:
        """Return tasks whose time windows (due_time + duration) overlap another task."""
        pending = sorted(
            [t for t in self.task_queue if t.status == TaskStatus.PENDING],
            key=lambda t: t.due_time,
        )
        conflicts: list[Task] = []
        for i in range(len(pending) - 1):
            current, nxt = pending[i], pending[i + 1]
            current_end = current.due_time + timedelta(minutes=current.duration)
            if current_end > nxt.due_time:
                if current not in conflicts:
                    conflicts.append(current)
                if nxt not in conflicts:
                    conflicts.append(nxt)
        return conflicts

    def generate_reminders(self) -> list[str]:
        """Return human-readable reminder strings for overdue and upcoming tasks."""
        reminders: list[str] = []
        for task in self.task_queue:
            if task.status != TaskStatus.PENDING:
                continue
            when = task.due_time.strftime("%H:%M")
            if task.is_overdue(self.current_time):
                reminders.append(f"OVERDUE: {task.type.value} for {task.pet.name} (was due {when})")
            else:
                reminders.append(f"Upcoming: {task.type.value} for {task.pet.name} at {when}")
        return reminders
