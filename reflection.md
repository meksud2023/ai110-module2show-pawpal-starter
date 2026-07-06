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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
