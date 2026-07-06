# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

A user of PawPal+ can do three main things:

1. **Add a pet**, where the owner registers a pet with details like name, species, age, and medical notes.
2. **Schedule a task**, where the owner adds a care task (like a walk, feeding, or medication) for a pet and sets its due time and whether it repeats.
3. **View today's tasks**, where the owner sees all of the day's tasks across their pets, automatically sorted by priority so urgent items like an overdue medication show up first.

**a. Initial design**

My initial UML design was built around four classes, and I gave each one a clear job:

- **Owner** represents the app user. It holds basic contact info and a list of the pets it owns, and it handles the high-level actions like adding or removing pets, viewing the daily schedule, and marking tasks complete.
- **Pet** represents a single animal. It holds descriptive and medical details (species, age, weight, notes) and owns the list of care tasks that belong to it. Its job is managing its own tasks and reporting a medical summary.
- **Task** represents one unit of care work, such as a feeding, walk, medication, or appointment. It is the object the scheduler prioritizes, so it holds its due time, duration, status, recurrence info, and a priority score, and it knows whether it is overdue and how to compute its own priority.
- **Scheduler** is the algorithmic "brain." It does not hold pet data. Instead it takes tasks, orders them by priority, builds the daily plan, detects time conflicts, and generates reminders.

The relationships were straightforward: an Owner owns many Pets, a Pet has many Tasks, and the Scheduler manages many Tasks. I used Python dataclasses for the data-heavy objects (Owner, Pet, Task) and a regular class for the Scheduler since it is more about behavior than data.

**b. Design changes**

After reviewing the skeleton, I made a couple of changes based on AI feedback.

- I **added a `Scheduler.add_tasks(tasks)` method**. My original design connected Owner to Pet to Task, and Scheduler to Task, as two separate chains, but there was no link between them. Tasks lived on a pet, yet the scheduler had no way to receive them. So I added a batch-loading method that lets the app collect all the tasks across an owner's pets and feed them into the scheduler in one step. That closed the gap between the data classes and the scheduling logic.

- I **added an `Owner.get_all_tasks()` aggregator**. When I started implementing the scheduler, I needed a clean way for it to get tasks. Instead of letting the Scheduler reach into each `Pet.tasks` list (which would tie it to the Pet's internal structure), I gave the Owner a method that gathers every task across its pets into one list. Now the Scheduler just calls `add_tasks(owner.get_all_tasks())`, which keeps the two decoupled.

I also noticed a consistency issue that I chose not to fully restructure. Tasks are referenced both in `Pet.tasks` and in the `Scheduler.task_queue`, so the two can drift apart if one is updated and the other isn't. I decided to treat the pet's list as the source of truth and rebuild the scheduler's queue when needed, rather than keeping two permanent copies. Re-sorting the queue as a plain list is fine here because a single owner only has a small number of tasks in a day.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler weighs three things when it orders a day's tasks:

1. **Urgency (overdue).** Any task past its due time gets pushed to the top, because a missed medication or feeding is the most time-sensitive problem.
2. **Priority by task type.** Each type has a weight, medication (100), then appointment (80), then feeding (60), then walk (40), so health-critical care outranks optional care.
3. **Due time.** Among tasks of equal priority, the earlier one comes first.

I decided urgency mattered most because for a pet owner the real cost is forgetting something important, not doing things in a slightly different order. Task type came second because it reflects how serious the consequences are, since a skipped pill matters more than a skipped walk. Time is just the natural tiebreaker.

**b. Tradeoffs**

The clearest tradeoff was in conflict detection. My first version only compared tasks that were next to each other after sorting by time. It was fast (O(n log n)), but it was wrong, because it missed a long task like a 45-minute feeding overlapping a later task that wasn't directly next to it. I switched to a sweep that compares each task to the ones after it and stops as soon as one starts after the current task ends. That version is worst case O(n squared), but the early stop keeps it close to linear for realistic schedules, and most importantly it is correct.

That tradeoff makes sense here because a pet owner only has a handful of tasks per day, so the extra cost is tiny, and correctness matters far more than speed at this scale.

A second tradeoff is in how I handle recurring tasks. I only create the next occurrence when the current one is completed, rather than expanding a whole week ahead of time. This keeps the logic simple and always in sync, but the cost is that you can't preview future recurrences until the earlier ones are done. For a daily-use planner that felt like an acceptable limit.

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant across the whole project, but for different jobs at each stage:

- Design brainstorming, where I listed the core classes and their attributes and methods, and stress-tested the relationships before writing any code.
- Scaffolding, where I turned the UML into dataclass stubs and then filled in the method logic.
- Algorithm design, where I compared approaches for sorting, conflict detection, and recurrence, and weighed their clarity against their efficiency.
- Testing, where I drafted a test plan covering happy paths and edge cases and then wrote the pytest functions.
- Documentation, including docstrings, the README, and this reflection.

The prompts that helped most were specific and design-focused, not "just write this for me." For example, asking "how should the Scheduler retrieve tasks from the Owner's pets?" led to a clean `get_all_tasks()` aggregator instead of the Scheduler reaching into pet internals. Asking for tradeoffs, like "give me a lightweight conflict strategy that warns instead of crashing," gave me better options than asking for a single answer.

**b. Judgment and verification**

The clearest moment I did not accept a suggestion as-is was the conflict detection algorithm. The first version only compared tasks that were next to each other after sorting. It looked correct and it was efficient, but when I ran the demo I saw it silently missed a 45-minute feeding that overlapped a later, non-adjacent walk. I rejected it and replaced it with an interval sweep that compares each task to all the following ones until one starts after it ends. Later I also caught that it treated two zero-duration tasks at the exact same time as not conflicting, and I fixed the comparison.

I verified AI suggestions by running them, not just reading them. The CLI demo is what exposed the missing conflict, and the pytest suite of 10 tests pins down each behavior, including the edge cases, so a regression would fail loudly. I also refactored a suggestion that put the recurrence rollover only in `Scheduler.complete_task`, because it left `Owner.mark_task_complete` quietly not rolling over. I pulled both paths onto one shared `Task` method so they behave the same.

---

## 4. Testing and Verification

**a. What you tested**

I wrote 10 automated tests in `tests/test_pawpal.py` covering:

- Core objects, where completing a task changes its status and adding a task grows the pet's list.
- Sorting, where `sort_by_time()` returns tasks in chronological order.
- Filtering, where `filter_tasks()` narrows by pet, status, or both.
- Priority, where an overdue medication outranks an earlier but lower-priority task.
- Conflict detection, where overlapping windows are flagged and two tasks at the exact same time raise a warning without crashing.
- Recurrence, where a daily task rolls over to the next day, a weekly task adds 7 days, and both the Owner and Scheduler completion paths behave the same way.
- An edge case, where a pet or owner with no tasks returns empty results instead of erroring.

These mattered because they cover the parts most likely to break: the ordering logic (which is the whole point of the app), the conflict edge cases (same time versus back to back), and the recurrence consistency between the two completion paths, which is exactly the bug I had to fix earlier.

**b. Confidence**

I'm fairly confident, about 4 out of 5. All 10 tests pass, and they cover every core behavior plus the key edge cases. I held back one star because the tests use small, hand-built scenarios. With more time I would test larger schedules, invalid or misspelled recurrence rules like "biweekly", and tasks that cross midnight, since date boundaries feel like the place a hidden bug is most likely to be hiding.

---

## 5. Reflection

**a. What went well**

What I'm most satisfied with is the separation between the logic layer and the UI. Because all the intelligence lives in `pawpal_system.py` and was verified from the CLI first, wiring it into Streamlit at the end was mostly display code, and the hard parts were already tested. The prioritization logic, where an overdue medication rises to the top, is the feature I'm proudest of, because it makes the app feel genuinely smart instead of being just a list.

**b. What you would improve**

If I had another iteration, I'd rethink how tasks are stored. Right now a task lives both in `Pet.tasks` and in the `Scheduler.task_queue`, and I keep them in sync by treating the pet's list as the source of truth and rebuilding the queue. That works, but a cleaner design would have the Scheduler always read live from the Owner instead of holding its own copy, which would remove the risk of drift entirely. I'd also add a "generate ahead" option for recurring tasks so an owner could preview the week.

**c. Key takeaway**

The biggest thing I learned is what it actually means to be the lead architect when you're working with a powerful AI assistant. The AI is great at producing plausible, working-looking code quickly, but "looks right" is not the same as "is right." My real job was to make the design decisions about where logic belongs and which tradeoffs to accept, to run and test what the AI produced instead of trusting it, and to catch the subtle bugs it introduced, like the adjacent-only conflict check and the inconsistent completion paths. Using separate chat sessions for each phase, one for design, one for algorithms, and one for testing, kept each conversation focused and stopped earlier context from muddying later decisions. That made it a lot easier to stay in control of the overall architecture instead of letting the AI drift it around.
