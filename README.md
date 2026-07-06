# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## ✨ Features

PawPal+ turns a list of care tasks into a smart daily plan:

- **Priority scheduling** — tasks are ordered by urgency (overdue first), then by task-type importance (medication > appointment > feeding > walk), then by time of day.
- **Sort by time** — a one-click chronological view of the same tasks (`Scheduler.sort_by_time()`).
- **Filtering** — narrow the plan by pet, by completion status, or both (`Scheduler.filter_tasks()`).
- **Conflict warnings** — detects tasks whose times overlap *or* fall at the exact same moment, and reports each clash as a plain-language warning instead of crashing (`Scheduler.detect_conflicts()` / `get_conflict_warnings()`).
- **Daily / weekly recurrence** — completing a recurring task automatically schedules its next occurrence using `timedelta` (daily = +1 day, weekly = +7 days).
- **Multi-pet support** — one owner can track several pets, and the scheduler aggregates every pet's tasks into a single plan.

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

Run the automated test suite from the project root with:

```bash
python -m pytest
```

**What the tests cover** (`tests/test_pawpal.py`):

- **Core objects** — completing a task changes its status; adding a task grows the pet's list.
- **Sorting** — `sort_by_time()` returns tasks in chronological order.
- **Filtering** — `filter_tasks()` narrows by pet, status, or both.
- **Priority** — an overdue medication outranks an earlier low-priority task.
- **Conflict detection** — overlapping windows are flagged, and two tasks at the *exact same time* raise a warning without crashing.
- **Recurrence** — completing a daily task creates the next day's task; the weekly rule adds 7 days; both the Owner and Scheduler completion paths roll over consistently.
- **Edge case** — a pet/owner with no tasks returns empty results and never errors.

Successful test run:

```
============================= test session starts =============================
platform win32 -- Python 3.10.1, pytest-9.0.3, pluggy-1.6.0
collected 10 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 10%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 20%]
tests/test_pawpal.py::test_sort_by_time_is_chronological PASSED          [ 30%]
tests/test_pawpal.py::test_filter_by_pet_and_status PASSED               [ 40%]
tests/test_pawpal.py::test_detect_conflicts_finds_overlap PASSED         [ 50%]
tests/test_pawpal.py::test_same_time_conflict_produces_warning PASSED    [ 60%]
tests/test_pawpal.py::test_recurring_task_rolls_over_on_completion PASSED [ 70%]
tests/test_pawpal.py::test_get_next_task_prioritizes_overdue_medication PASSED [ 80%]
tests/test_pawpal.py::test_empty_schedule_does_not_crash PASSED          [ 90%]
tests/test_pawpal.py::test_owner_completion_path_also_rolls_over PASSED  [100%]

============================= 10 passed in 0.07s ==============================
```

**Confidence Level: ★★★★☆ (4/5)**

All 10 tests pass and cover every core behavior plus the key edge cases (same-time
conflicts, empty schedules, both recurrence paths). I held back one star because the
tests use small, hand-built scenarios — I'd want to test larger schedules, invalid or
malformed recurrence rules, and tasks spanning across midnight before rating it 5/5.

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

### Running it

- **Web UI:** `streamlit run app.py`
- **CLI demo:** `python main.py`

### What the UI lets you do

The Streamlit app ([app.py](app.py)) is a thin layer over the logic in
[pawpal_system.py](pawpal_system.py). A user can:

1. Set the **owner name** and **add one or more pets** (name + species).
2. **Add tasks** for a pet — choosing the type (feeding / walk / medication / appointment),
   time, duration, and whether it recurs (daily / weekly / hourly).
3. View **Today's Schedule** as a table, and toggle the order between **Priority** and
   **Time of day**, or **filter** to a single pet.
4. See **conflict warnings** surfaced at the top of the schedule the moment two tasks clash.
5. **Mark a task complete** — and if it was recurring, watch the next occurrence get
   scheduled automatically.

### Example workflow

> Add pet "Mochi" → add a **medication at 08:00** and a **walk at 11:00** → add pet
> "Luna" with a **feeding at 10:00** → open **Today's Schedule**. The overdue medication
> sorts to the top by priority; switching to *Time of day* reorders it chronologically;
> booking two tasks at the same time raises a warning banner. Completing Luna's daily
> medication auto-schedules tomorrow's.

### Key Scheduler behaviors shown
- **Sorting** — priority-and-urgency order vs. chronological order.
- **Filtering** — per-pet and per-status views.
- **Conflict warnings** — same-time and overlapping tasks flagged without crashing.
- **Recurrence** — automatic rollover of daily/weekly tasks on completion.

### Sample CLI output (`python main.py`)

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

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
