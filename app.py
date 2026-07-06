"""PawPal+ Streamlit UI.

A thin presentation layer over the logic in pawpal_system.py. All scheduling
intelligence (sorting, filtering, conflict detection, recurrence) lives in the
Scheduler/Task classes; this file only collects input and displays results.
"""

from datetime import datetime

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler, TaskType, TaskStatus

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A smart pet care planner — schedules and prioritizes daily tasks.")

# --- Session state: keep one Owner (with its pets/tasks) alive across reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_id="o1", name="Jordan")
if "task_counter" not in st.session_state:
    st.session_state.task_counter = 0

owner: Owner = st.session_state.owner


def next_task_id() -> str:
    st.session_state.task_counter += 1
    return f"t{st.session_state.task_counter}"


# --- Owner ---
owner.name = st.text_input("Owner name", value=owner.name)

# --- Add a pet ---
st.subheader("🐾 Pets")
with st.form("add_pet", clear_on_submit=True):
    c1, c2 = st.columns(2)
    pet_name = c1.text_input("Pet name", value="Mochi")
    species = c2.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet") and pet_name:
        owner.add_pet(Pet(pet_id=f"p{len(owner.pets) + 1}", name=pet_name, species=species))

if owner.pets:
    st.write("Current pets:", ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("Add a pet to get started.")

# --- Add a task ---
if owner.pets:
    st.subheader("➕ Add a Task")
    with st.form("add_task", clear_on_submit=True):
        c1, c2 = st.columns(2)
        pet_name = c1.selectbox("Pet", [p.name for p in owner.pets])
        task_type = c2.selectbox("Type", [t.value for t in TaskType])
        c3, c4 = st.columns(2)
        task_time = c3.time_input("Time")
        duration = c4.number_input("Duration (min)", min_value=0, max_value=240, value=30)
        recurring = st.checkbox("Recurring?")
        rule = st.selectbox("Repeat", ["daily", "weekly", "hourly"], disabled=not recurring)
        if st.form_submit_button("Add task"):
            pet = next(p for p in owner.pets if p.name == pet_name)
            due = datetime.combine(datetime.now().date(), task_time)
            pet.add_task(Task(
                task_id=next_task_id(),
                type=TaskType(task_type),
                pet=pet,
                due_time=due,
                is_recurring=recurring,
                recurrence_rule=rule if recurring else "",
                duration=int(duration),
            ))

# --- Today's schedule (uses the Scheduler) ---
st.divider()
st.subheader("📋 Today's Schedule")

now = datetime.now()
scheduler = Scheduler(current_time=now)
scheduler.add_tasks(owner.get_all_tasks())

# Conflict warnings first — the most helpful thing for an owner to see up top.
warnings = scheduler.get_conflict_warnings()
for w in warnings:
    st.warning("⚠️ " + w.replace("WARNING: ", ""))
if not warnings and owner.get_all_tasks():
    st.success("✅ No scheduling conflicts today.")

# Controls: sort mode + pet filter (both driven by Scheduler methods).
c1, c2 = st.columns(2)
sort_mode = c1.radio("Sort by", ["Priority", "Time of day"], horizontal=True)
pet_filter = c2.selectbox("Show", ["All pets"] + [p.name for p in owner.pets])

plan = scheduler.get_daily_plan(now)  # today's pending tasks, priority order
if pet_filter != "All pets":
    plan = [t for t in plan if t.pet.name == pet_filter]
if sort_mode == "Time of day":
    plan = sorted(plan, key=lambda t: t.due_time)

if plan:
    rows = [
        {
            "Time": t.due_time.strftime("%H:%M"),
            "Task": t.type.value,
            "Pet": t.pet.name,
            "Priority": t.calculate_priority(),
            "Status": "OVERDUE" if t.is_overdue(now) else "pending",
        }
        for t in plan
    ]
    st.table(rows)

    nxt = scheduler.get_next_task()
    if nxt:
        st.success(f"👉 Next up: **{nxt.type.value}** for **{nxt.pet.name}** "
                   f"at {nxt.due_time.strftime('%H:%M')}")
else:
    st.info("No pending tasks for today. Add a task above.")

# --- Mark a task complete (shows recurrence rollover) ---
pending = scheduler.filter_tasks(status=TaskStatus.PENDING)
if pending:
    st.subheader("✔️ Mark a task done")
    labels = {f"{t.type.value} — {t.pet.name} @ {t.due_time.strftime('%H:%M')}": t
              for t in pending}
    choice = st.selectbox("Task", list(labels.keys()))
    if st.button("Complete"):
        done = labels[choice]
        rolled = owner.mark_task_complete(done)  # rolls over if recurring
        if rolled is not None:
            st.success(f"Done! Recurring task re-scheduled for "
                       f"{rolled.due_time.strftime('%b %d %H:%M')}.")
        else:
            st.success("Task marked complete.")
        st.rerun()
