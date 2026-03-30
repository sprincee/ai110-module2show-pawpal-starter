import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("PawPal+")
st.caption("Smart pet care scheduling.")

# Session state bootstrap
if "owner" not in st.session_state:
    st.session_state.owner = Owner("My Household")

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

# Sidebar: Add Pet
with st.sidebar:
    st.header("Add a Pet")
    pet_name = st.text_input("Pet Name")
    pet_species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
    pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
    if st.button("Add Pet"):
        if pet_name.strip():
            if owner.get_pet(pet_name.strip()):
                st.error(f"'{pet_name}' already exists.")
            else:
                owner.add_pet(Pet(pet_name.strip(), pet_species, int(pet_age)))
                st.success(f"Added {pet_name}.")
                st.rerun()
        else:
            st.warning("Enter a pet name.")

    st.divider()

    # Sidebar: Add Task
    st.header("Schedule a Task")
    if owner.pets:
        task_pet = st.selectbox("For Pet", [p.name for p in owner.pets])
        task_desc = st.text_input("Description")
        task_time = st.time_input("Time")
        task_freq = st.selectbox("Frequency", ["once", "daily", "weekly"])
        task_date = st.date_input("Date", value=date.today())
        if st.button("Add Task"):
            if task_desc.strip():
                pet = owner.get_pet(task_pet)
                pet.add_task(Task(task_desc.strip(), task_time.strftime("%H:%M"), task_freq, task_pet, task_date))
                st.success(f"Task added for {task_pet}.")
                st.rerun()
            else:
                st.warning("Enter a task description.")
    else:
        st.info("Add a pet first.")

    st.divider()

    # Sidebar: Remove Pet
    if owner.pets:
        st.header("Remove a Pet")
        remove_name = st.selectbox("Select Pet", [p.name for p in owner.pets], key="remove")
        if st.button("Remove Pet"):
            owner.remove_pet(remove_name)
            st.success(f"Removed {remove_name}.")
            st.rerun()

# Main area: stop early if no pets
if not owner.pets:
    st.info("Add your first pet in the sidebar to get started.")
    st.stop()

# Metrics
all_tasks = scheduler.get_all_tasks()
today_tasks = scheduler.todays_schedule()
conflicts = scheduler.detect_conflicts()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Pets", len(owner.pets))
col2.metric("Total Tasks", len(all_tasks))
col3.metric("Due Today", len(today_tasks))
col4.metric("Conflicts", len(conflicts))

st.divider()

# Conflict warnings
if conflicts:
    st.subheader("Scheduling Conflicts")
    for warning in conflicts:
        st.warning(warning)

# Tabs
tab1, tab2, tab3 = st.tabs(["Today's Schedule", "My Pets", "All Tasks"])

with tab1:
    st.subheader(f"Schedule for {date.today().strftime('%A, %B %d')}")
    if not today_tasks:
        st.info("No tasks scheduled for today.")
    else:
        for task in today_tasks:
            col_text, col_btn = st.columns([5, 1])
            with col_text:
                status = "done" if task.completed else "pending"
                st.write(f"**{task.time}** — {task.description} | {task.pet_name} | {task.frequency} | {status}")
            with col_btn:
                if not task.completed:
                    if st.button("Done", key=f"done_{id(task)}"):
                        scheduler.mark_task_complete(task)
                        st.rerun()

with tab2:
    st.subheader("Your Pets")
    for pet in owner.pets:
        with st.expander(f"{pet.name} — {pet.species}, age {pet.age}"):
            pet_tasks = scheduler.sort_by_time(scheduler.filter_by_pet(pet.name))
            if not pet_tasks:
                st.write("No tasks yet.")
            else:
                for t in pet_tasks:
                    status = "done" if t.completed else "pending"
                    st.write(f"**{t.time}** — {t.description} | {t.frequency} | due {t.due_date} | {status}")

with tab3:
    st.subheader("All Tasks")
    col_a, col_b = st.columns(2)
    with col_a:
        filter_pet = st.selectbox("Filter by Pet", ["All"] + [p.name for p in owner.pets])
    with col_b:
        filter_status = st.selectbox("Filter by Status", ["All", "Incomplete", "Completed"])

    filtered = all_tasks
    if filter_pet != "All":
        filtered = scheduler.filter_by_pet(filter_pet, filtered)
    if filter_status == "Incomplete":
        filtered = scheduler.filter_by_status(False, filtered)
    elif filter_status == "Completed":
        filtered = scheduler.filter_by_status(True, filtered)

    filtered = scheduler.sort_by_time(filtered)

    if not filtered:
        st.info("No tasks match your filters.")
    else:
        for task in filtered:
            status = "done" if task.completed else "pending"
            st.write(f"**{task.time}** — {task.description} | {task.pet_name} | {task.frequency} | due {task.due_date} | {status}")

st.divider()
st.caption("PawPal+ — keep your pets happy and healthy.")