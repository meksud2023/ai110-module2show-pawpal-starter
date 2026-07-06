"""
PawPal+ CLI demo script.

A temporary testing ground to verify the backend logic (pawpal_system.py) works
from the terminal before connecting it to the Streamlit UI. Run with:

    python main.py
"""

from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler, TaskType


def print_schedule(title: str, tasks, current_time: datetime) -> None:
    """Print a clean, readable schedule table to the terminal."""
    print(f"\n{title}")
    print("=" * 52)
    if not tasks:
        print("  (nothing scheduled)")
        return
    print(f"  {'TIME':<7} {'TASK':<12} {'PET':<8} {'PRIORITY':<9} STATUS")
    print("  " + "-" * 48)
    for t in tasks:
        status = "OVERDUE" if t.is_overdue(current_time) else "pending"
        print(
            f"  {t.due_time.strftime('%H:%M'):<7} "
            f"{t.type.value:<12} {t.pet.name:<8} "
            f"{t.priority:<9} {status}"
        )


def main() -> None:
    # Fixed "now" so the demo is reproducible.
    now = datetime(2026, 7, 6, 9, 0)

    # 1. Create an owner.
    owner = Owner(owner_id="o1", name="Jordan")

    # 2. Create at least two pets and register them.
    mochi = Pet(pet_id="p1", name="Mochi", species="dog", age=3, weight=12.5)
    luna = Pet(pet_id="p2", name="Luna", species="cat", age=5, weight=4.2)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # 3. Add tasks with different times across the two pets.
    #    Mochi's feeding (45 min) overlaps his walk to demonstrate conflict detection.
    #    Luna's medication is recurring (daily).
    mochi.add_task(Task("t1", TaskType.MEDICATION, mochi, now - timedelta(hours=1)))  # overdue
    mochi.add_task(Task("t2", TaskType.FEEDING, mochi, now + timedelta(hours=1), duration=45))
    mochi.add_task(Task("t3", TaskType.WALK, mochi, now + timedelta(hours=1, minutes=30)))
    luna.add_task(Task("t4", TaskType.FEEDING, luna, now + timedelta(hours=1)))
    luna.add_task(Task("t5", TaskType.MEDICATION, luna, now + timedelta(hours=2),
                       is_recurring=True, recurrence_rule="daily"))
    # Two tasks booked at the EXACT same time (13:00) to demonstrate the
    # same-time conflict warning, even though neither has a duration.
    mochi.add_task(Task("t6", TaskType.WALK, mochi, now + timedelta(hours=4)))
    luna.add_task(Task("t7", TaskType.APPOINTMENT, luna, now + timedelta(hours=4)))

    # 4. The Scheduler pulls all tasks from the owner and orders them.
    scheduler = Scheduler(current_time=now)
    scheduler.add_tasks(owner.get_all_tasks())

    print("PawPal+ | Owner:", owner.name, f"| Pets: {mochi.name}, {luna.name}")

    # Priority view (the "smart" ordering).
    print_schedule("Today's Schedule (ordered by priority)", scheduler.get_daily_plan(now), now)

    nxt = scheduler.get_next_task()
    print(f"\nNext up: {nxt.type.value} for {nxt.pet.name} at {nxt.due_time.strftime('%H:%M')}")

    # Sort-by-time view.
    print_schedule("Same tasks, sorted by time of day", scheduler.sort_by_time(), now)

    # Filter view: just Mochi's tasks.
    print_schedule(f"Filtered: only {mochi.name}'s tasks",
                   scheduler.filter_tasks(pet=mochi), now)

    # Conflict detection: print a lightweight warning per clash (never crashes).
    print("\nTime conflicts")
    print("=" * 52)
    warnings = scheduler.get_conflict_warnings()
    if not warnings:
        print("  (none)")
    for w in warnings:
        print(" ", w)

    # Recurring rollover: completing Luna's daily med schedules tomorrow's automatically.
    luna_med = luna.tasks[1]
    next_med = scheduler.complete_task(luna_med)
    print("\nRecurring task rollover")
    print("=" * 52)
    print(f"  Completed {luna_med.type.value} for {luna.name} "
          f"(due {luna_med.due_time.strftime('%b %d %H:%M')})")
    print(f"  Auto-scheduled next: due {next_med.due_time.strftime('%b %d %H:%M')}")


if __name__ == "__main__":
    main()
