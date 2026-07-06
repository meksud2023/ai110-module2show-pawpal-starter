"""Tests for the PawPal+ logic layer (pawpal_system.py)."""

import os
import sys
from datetime import datetime, timedelta

# Make the project root importable so `pawpal_system` is found when running pytest.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Owner, Pet, Task, TaskType, TaskStatus, Scheduler


def test_mark_complete_changes_status():
    """Task Completion: mark_complete() should set the task's status to COMPLETED."""
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    task = Task("t1", TaskType.WALK, pet, datetime(2026, 7, 6, 9, 0))

    assert task.status == TaskStatus.PENDING  # starts pending

    task.mark_complete()

    assert task.status == TaskStatus.COMPLETED


def test_adding_task_increases_pet_task_count():
    """Task Addition: adding a task to a Pet should increase its task count by one."""
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    assert len(pet.tasks) == 0  # starts empty

    task = Task("t1", TaskType.FEEDING, pet, datetime(2026, 7, 6, 10, 0))
    pet.add_task(task)

    assert len(pet.tasks) == 1


# --- Phase 3: smart scheduling features ---

def test_sort_by_time_is_chronological():
    """Sorting: sort_by_time() returns tasks earliest-due-time first."""
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    late = Task("t1", TaskType.WALK, pet, datetime(2026, 7, 6, 15, 0))
    early = Task("t2", TaskType.FEEDING, pet, datetime(2026, 7, 6, 8, 0))
    sched = Scheduler(current_time=datetime(2026, 7, 6, 7, 0))
    sched.add_tasks([late, early])  # added out of order

    ordered = sched.sort_by_time()

    assert [t.task_id for t in ordered] == ["t2", "t1"]  # early before late


def test_filter_by_pet_and_status():
    """Filtering: filter_tasks() narrows by pet and by status."""
    mochi = Pet(pet_id="p1", name="Mochi", species="dog")
    luna = Pet(pet_id="p2", name="Luna", species="cat")
    now = datetime(2026, 7, 6, 9, 0)
    t1 = Task("t1", TaskType.WALK, mochi, now)
    t2 = Task("t2", TaskType.FEEDING, luna, now)
    t3 = Task("t3", TaskType.FEEDING, mochi, now)
    t3.mark_complete()
    sched = Scheduler(current_time=now)
    sched.add_tasks([t1, t2, t3])

    assert {t.task_id for t in sched.filter_tasks(pet=mochi)} == {"t1", "t3"}
    assert {t.task_id for t in sched.filter_tasks(status=TaskStatus.PENDING)} == {"t1", "t2"}
    # combined: Mochi's pending tasks only
    assert {t.task_id for t in sched.filter_tasks(pet=mochi, status=TaskStatus.PENDING)} == {"t1"}


def test_detect_conflicts_finds_overlap():
    """Conflicts: an overlapping pair is detected, non-overlapping is not."""
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    now = datetime(2026, 7, 6, 10, 0)
    feeding = Task("t1", TaskType.FEEDING, pet, now, duration=45)   # 10:00-10:45
    walk = Task("t2", TaskType.WALK, pet, now + timedelta(minutes=30))  # 10:30
    sched = Scheduler(current_time=now)
    sched.add_tasks([feeding, walk])

    conflicts = sched.detect_conflicts()

    assert len(conflicts) == 1
    assert {conflicts[0][0].task_id, conflicts[0][1].task_id} == {"t1", "t2"}


def test_same_time_conflict_produces_warning():
    """Conflicts: two zero-duration tasks at the same time are flagged with a warning."""
    mochi = Pet(pet_id="p1", name="Mochi", species="dog")
    luna = Pet(pet_id="p2", name="Luna", species="cat")
    now = datetime(2026, 7, 6, 13, 0)
    a = Task("t1", TaskType.WALK, mochi, now)         # same time, no duration
    b = Task("t2", TaskType.APPOINTMENT, luna, now)   # same time, no duration
    solo = Task("t3", TaskType.FEEDING, mochi, now + timedelta(hours=1))
    sched = Scheduler(current_time=now)
    sched.add_tasks([a, b, solo])

    warnings = sched.get_conflict_warnings()

    assert len(warnings) == 1               # only the same-time pair clashes
    assert "WARNING" in warnings[0]
    # back-to-back / separate task is not flagged
    assert len(sched.detect_conflicts()) == 1


def test_recurring_task_rolls_over_on_completion():
    """Recurring: completing a daily task creates its next occurrence one day later."""
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    now = datetime(2026, 7, 6, 8, 0)
    daily = Task("t1", TaskType.MEDICATION, pet, now,
                 is_recurring=True, recurrence_rule="daily")
    pet.add_task(daily)
    sched = Scheduler(current_time=now)
    sched.add_task(daily)

    next_task = sched.complete_task(daily)

    assert daily.status == TaskStatus.COMPLETED
    assert next_task is not None
    assert next_task.due_time == now + timedelta(days=1)
    assert next_task in pet.tasks  # kept in sync with the pet's list
    assert next_task.status == TaskStatus.PENDING  # the new one is not done yet


def test_get_next_task_prioritizes_overdue_medication():
    """Priority: an overdue medication outranks an earlier-but-lower-priority walk."""
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    now = datetime(2026, 7, 6, 9, 0)
    overdue_med = Task("t1", TaskType.MEDICATION, pet, now - timedelta(hours=1))
    upcoming_walk = Task("t2", TaskType.WALK, pet, now + timedelta(hours=1))
    sched = Scheduler(current_time=now)
    sched.add_tasks([upcoming_walk, overdue_med])  # added lower-priority first

    assert sched.get_next_task().task_id == "t1"  # the overdue medication wins


def test_empty_schedule_does_not_crash():
    """Edge case: an owner/pet with no tasks returns empty results, never an error."""
    owner = Owner(owner_id="o1", name="Jordan")
    owner.add_pet(Pet(pet_id="p1", name="Mochi", species="dog"))
    sched = Scheduler(current_time=datetime(2026, 7, 6, 9, 0))
    sched.add_tasks(owner.get_all_tasks())  # nothing to add

    assert owner.get_all_tasks() == []
    assert sched.get_daily_plan(datetime(2026, 7, 6, 9, 0)) == []
    assert sched.get_next_task() is None          # no task, no crash
    assert sched.detect_conflicts() == []
    assert sched.get_conflict_warnings() == []


def test_owner_completion_path_also_rolls_over():
    """Consistency: completing via the Owner path rolls over recurring tasks too."""
    pet = Pet(pet_id="p1", name="Luna", species="cat")
    now = datetime(2026, 7, 6, 8, 0)
    weekly = Task("t1", TaskType.MEDICATION, pet, now,
                  is_recurring=True, recurrence_rule="weekly")
    pet.add_task(weekly)
    owner = Owner(owner_id="o1", name="Jordan")
    owner.add_pet(pet)

    next_task = owner.mark_task_complete(weekly)

    assert weekly.status == TaskStatus.COMPLETED
    assert next_task is not None
    assert next_task.due_time == now + timedelta(weeks=1)  # +7 days for weekly
    assert next_task in pet.tasks
