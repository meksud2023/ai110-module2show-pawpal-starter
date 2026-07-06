"""Tests for the PawPal+ logic layer (pawpal_system.py)."""

import os
import sys
from datetime import datetime

# Make the project root importable so `pawpal_system` is found when running pytest.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Pet, Task, TaskType, TaskStatus


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
