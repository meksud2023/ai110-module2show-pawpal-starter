# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

A user of PawPal+ can perform three main actions:

1. **Add a pet** — the owner registers a pet with details like name, species, age, and medical notes.
2. **Schedule a task** — the owner adds a care task (such as a walk, feeding, or medication) for a pet, setting its due time and whether it repeats.
3. **View today's tasks** — the owner sees all of the day's tasks across their pets, automatically sorted by priority so urgent items (like an overdue medication) appear first.

**a. Initial design**

My initial UML design centered on four classes, each with a clear responsibility:

- **Owner** — represents the app user. It holds basic contact info and a list of the pets it owns, and is responsible for high-level actions like adding/removing pets, viewing the daily schedule, and marking tasks complete.
- **Pet** — represents a single animal. It holds descriptive and medical details (species, age, weight, notes) and owns the list of care tasks that belong to it. Its responsibility is managing its own tasks and reporting a medical summary.
- **Task** — represents one unit of care work (a feeding, walk, medication, or appointment). It is the object the scheduler prioritizes, so it holds its due time, duration, status, recurrence info, and a priority score, and is responsible for knowing whether it is overdue and computing its own priority.
- **Scheduler** — the algorithmic "brain." It does not hold pet data; instead it takes tasks, orders them by priority, builds the daily plan, detects time conflicts, and generates reminders.

The relationships were: an Owner *owns* many Pets, a Pet *has* many Tasks, and the Scheduler *manages* many Tasks. I used Python dataclasses for the data-heavy objects (Owner, Pet, Task) and a regular class for Scheduler since it is behavior-driven.

**b. Design changes**

After reviewing the skeleton, I made one change based on AI feedback:

- **Added a `Scheduler.add_tasks(tasks)` method.** My original design connected `Owner → Pet → Task` and `Scheduler → Task` as two separate chains, but there was no link between them — tasks lived on a pet, yet the scheduler had no way to receive them. I added a batch-loading method so the app layer can collect all tasks across an owner's pets and feed them into the scheduler in one step. This closes the missing relationship between the data classes and the scheduling logic.

- **Added an `Owner.get_all_tasks()` aggregator.** When implementing the scheduler, I needed a clean way for it to receive tasks. Rather than letting the Scheduler reach into each `Pet.tasks` list (which would tie it to the Pet structure), I gave the Owner a method that gathers every task across its pets into one list. The Scheduler then just calls `add_tasks(owner.get_all_tasks())`, keeping the two decoupled.

I also identified (but chose not to restructure) a consistency consideration: tasks are referenced both in `Pet.tasks` and in the `Scheduler.task_queue`, so updates must be kept in sync. I decided to treat the pet's list as the source of truth and rebuild the scheduler's queue when needed, rather than duplicating state permanently. Re-sorting the queue as a plain list is acceptable here because a single owner only has a small number of daily tasks.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers three constraints when ordering a day's tasks:

1. **Urgency (overdue):** any task past its due time is pushed to the top, because a missed medication or feeding is the most time-sensitive problem.
2. **Priority by task type:** each type has a weight — medication (100) > appointment (80) > feeding (60) > walk (40) — so health-critical care outranks optional care.
3. **Due time:** among tasks of equal priority, earlier ones come first.

I decided urgency mattered most because for a pet owner, the real cost is *forgetting* something important, not doing things in a slightly different order. Task type came second because it reflects how serious the consequences are (a skipped pill matters more than a skipped walk). Time is the natural tiebreaker.

**b. Tradeoffs**

One clear tradeoff is in **conflict detection**. My first version compared only *adjacent* tasks after sorting by time, which was fast (O(n log n)) but wrong — it missed a long task (e.g. a 45-minute feeding) overlapping a *non-adjacent* later task. I switched to a sweep that compares each task to the ones after it and stops as soon as one starts after the current task ends. This is worst-case O(n²), but the early stop keeps it close to linear for realistic schedules, and it is correct.

That tradeoff is reasonable here because a pet owner only has a handful of tasks per day, so the extra cost is negligible, and correctness matters far more than speed at this scale.

A second tradeoff is in **recurring tasks**: I generate the next occurrence only when the current one is completed ("on-completion"), rather than expanding a whole week ahead. This keeps the logic simple and always in sync, at the cost of not being able to preview future recurrences until earlier ones are done — an acceptable limit for a daily-use planner.

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant across the whole project, but for different jobs at each stage:

- **Design brainstorming:** listing the core classes and their attributes/methods, and pressure-testing the relationships before I wrote any code.
- **Scaffolding:** turning the UML into dataclass stubs, then filling in method logic.
- **Algorithm design:** comparing approaches for sorting, conflict detection, and recurrence, and weighing their clarity vs. efficiency.
- **Testing:** drafting a test plan (happy paths + edge cases) and writing the pytest functions.
- **Documentation:** docstrings, the README, and this reflection.

The most helpful prompts were **specific and design-oriented** rather than "write this for me." For example, asking *"how should the Scheduler retrieve tasks from the Owner's pets?"* led to a clean `get_all_tasks()` aggregator instead of the Scheduler reaching into pet internals. Asking for *tradeoffs* ("give me a lightweight conflict strategy that warns instead of crashing") produced better options than asking for a single answer.

**b. Judgment and verification**

The clearest moment I did **not** accept a suggestion as-is was the **conflict detection algorithm**. The first version only compared *adjacent* tasks after sorting — it looked correct and was efficient, but when I ran the demo I saw it silently missed a 45-minute feeding overlapping a non-adjacent later walk. I rejected it and replaced it with an interval sweep that compares each task to all following tasks until one starts after it ends. I also later caught that it treated two zero-duration tasks at the *exact same time* as non-conflicting, and fixed the comparison.

I verified AI suggestions by **running them, not just reading them**: the CLI demo exposed the missing conflict, and the pytest suite (10 tests) pins down each behavior — including the edge cases — so a regression would fail loudly. I also refactored an AI suggestion that put recurrence rollover only in `Scheduler.complete_task`, because it left `Owner.mark_task_complete` silently not rolling over; I consolidated both paths onto one shared `Task` method.

---

## 4. Testing and Verification

**a. What you tested**

I wrote 10 automated tests in `tests/test_pawpal.py` covering:

- **Core objects** — completing a task changes its status; adding a task grows the pet's list.
- **Sorting** — `sort_by_time()` returns tasks in chronological order.
- **Filtering** — `filter_tasks()` narrows by pet, status, or both.
- **Priority** — an overdue medication outranks an earlier, lower-priority task.
- **Conflict detection** — overlapping windows are flagged, and two tasks at the exact same time raise a warning without crashing.
- **Recurrence** — a daily task rolls over to the next day, a weekly task adds 7 days, and both the Owner and Scheduler completion paths behave identically.
- **Edge case** — a pet/owner with no tasks returns empty results instead of erroring.

These were important because they cover the parts most likely to break: the *ordering logic* (the whole point of the app), the *conflict edge cases* (same-time vs. back-to-back), and the *recurrence consistency* between two completion paths — exactly the bug I had to fix earlier.

**b. Confidence**

I am fairly confident — **4 out of 5**. All 10 tests pass, and they cover every core behavior plus the key edge cases. I held back one star because the tests use small, hand-built scenarios. With more time I would test **larger schedules**, **invalid or misspelled recurrence rules** (e.g. `"biweekly"`), and **tasks that cross midnight**, since date-boundary handling is where I'd most expect a hidden bug.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the **separation between the logic layer and the UI**. Because all the intelligence lives in `pawpal_system.py` and was verified from the CLI first, wiring it into Streamlit at the end was mostly display code — the hard parts were already tested. The prioritization logic (overdue medication surfacing to the top) is the feature I'm proudest of because it makes the app feel genuinely "smart" rather than just a list.

**b. What you would improve**

If I had another iteration I'd rethink how tasks are stored. Right now a task lives both in `Pet.tasks` and in the `Scheduler.task_queue`, and I keep them in sync by treating the pet's list as the source of truth and rebuilding the queue. That works, but a cleaner design would have the Scheduler always read live from the Owner rather than holding its own copy, removing the risk of drift entirely. I'd also add a "generate-ahead" option for recurring tasks so an owner can preview the week.

**c. Key takeaway**

The biggest thing I learned is what it means to be the **lead architect** when working with a powerful AI assistant. The AI is excellent at producing plausible, working-looking code quickly — but "looks right" is not "is right." My job was to make the design decisions (where logic belongs, which tradeoffs to accept), to *run and test* what the AI produced instead of trusting it, and to catch the subtle bugs it introduced (the adjacent-only conflict check, the inconsistent completion paths). Using **separate chat sessions per phase** — one for design, one for algorithms, one for testing — kept each conversation focused and stopped earlier context from muddying later decisions, which made it much easier to stay in control of the overall architecture rather than letting the AI drift it.
