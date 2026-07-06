# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Terminal output from running the CLI demo script (`python main.py`). This verifies the
backend logic works before it is connected to the Streamlit UI:

```
PawPal+ | Owner: Jordan | Pets: Mochi, Luna

Today's Schedule (ordered by priority)
====================================================
  TIME    TASK         PET      PRIORITY  STATUS
  ------------------------------------------------
  08:00   medication   Mochi    100       OVERDUE
  11:00   medication   Luna     100       pending
  13:00   appointment  Luna     80        pending
  10:00   feeding      Mochi    60        pending
  10:00   feeding      Luna     60        pending
  10:30   walk         Mochi    40        pending
  13:00   walk         Mochi    40        pending

Next up: medication for Mochi at 08:00

Same tasks, sorted by time of day
====================================================
  TIME    TASK         PET      PRIORITY  STATUS
  ------------------------------------------------
  08:00   medication   Mochi    100       OVERDUE
  10:00   feeding      Mochi    60        pending
  10:00   feeding      Luna     60        pending
  10:30   walk         Mochi    40        pending
  11:00   medication   Luna     100       pending
  13:00   walk         Mochi    40        pending
  13:00   appointment  Luna     80        pending

Filtered: only Mochi's tasks
====================================================
  TIME    TASK         PET      PRIORITY  STATUS
  ------------------------------------------------
  08:00   medication   Mochi    100       OVERDUE
  10:00   feeding      Mochi    60        pending
  10:30   walk         Mochi    40        pending
  13:00   walk         Mochi    40        pending

Time conflicts
====================================================
  WARNING: feeding for Mochi at 10:00 clashes with feeding for Luna at 10:00
  WARNING: feeding for Mochi at 10:00 clashes with walk for Mochi at 10:30
  WARNING: walk for Mochi at 13:00 clashes with appointment for Luna at 13:00

Recurring task rollover
====================================================
  Completed medication for Luna (due Jul 06 11:00)
  Auto-scheduled next: due Jul 07 11:00
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here

```

## 📐 Smarter Scheduling

PawPal+ adds simple algorithms on top of the core classes to make the day's plan
"smart." Each feature and the method that implements it:

### Sorting
- **Priority + urgency order** — `Scheduler.get_daily_plan(date)` sorts a day's pending
  tasks so overdue tasks come first, then by task-type priority
  (medication > appointment > feeding > walk), then by due time.
- **Chronological order** — `Scheduler.sort_by_time()` returns the same tasks ordered
  purely by clock time, for owners who prefer to read their day top to bottom.

### Filtering
- `Scheduler.filter_tasks(pet=None, status=None)` narrows the task list by pet, by
  completion status, or both (the two arguments are optional and combinable — e.g.
  "only Mochi's pending tasks"). Runs in a single O(n) pass.

### Conflict detection
- `Scheduler.detect_conflicts()` returns every pair of pending tasks whose times
  clash. It sorts by start time, then for each task scans the ones that follow and
  stops early once a task starts after the current one ends. Two tasks at the **exact
  same time** are always flagged (even with no duration), while genuinely back-to-back
  tasks are not.
- `Scheduler.get_conflict_warnings()` wraps that result into plain-text warning
  strings (`"WARNING: ... clashes with ..."`) and never raises — the program keeps
  running and simply reports each clash.

### Recurring tasks
- `Task.next_occurrence()` computes the next due time from the recurrence rule
  (`hourly` / `daily` / `weekly`) using `timedelta`.
- Completing a recurring task automatically schedules the next one. Both completion
  paths — `Owner.mark_task_complete(task)` and `Scheduler.complete_task(task)` —
  delegate to the shared `Task.mark_task_done_and_roll_over()`, so a recurring task
  always rolls over no matter how it is completed.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
