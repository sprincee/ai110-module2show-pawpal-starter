# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The three core actions a user needs to perform:
1. Add a pet — register a pet with name, species, and age
2. Schedule a task — assign a care activity (walk, feeding, medication) to a pet at a specific time and date
3. View today's schedule — see all tasks due today sorted by time, and mark them complete

I designed four classes based on the real-world entities involved in pet care:

- **Task** (dataclass) — the atomic unit of care. Stores what needs to happen (description), when (time, due_date), how often (frequency), and whether it is done (completed). Using a dataclass keeps it clean and avoids boilerplate.
- **Pet** — represents an animal. Holds identity info (name, species, age) and owns a list of Task objects. Responsible for adding and removing tasks from itself.
- **Owner** — represents the human user. Manages a collection of Pet objects and provides a method to aggregate all tasks across all pets.
- **Scheduler** — the intelligence layer. Takes an Owner as a dependency and provides sorting, filtering, conflict detection, and recurring task management. It does not own any data — it only operates on data owned by Owner and Pet.

**b. Design changes**

After building the initial skeletons I made three changes:

1. Added `filter_by_date()` and `todays_schedule()` to Scheduler — a dedicated today-filter is more useful than forcing the user to manually filter every time.
2. Made filtering methods accept an optional tasks parameter — this allows chaining (filter by pet, then sort) without re-fetching from the owner on every call.
3. Made `mark_complete()` return the next Task instead of just mutating completed — this makes recurrence logic composable and easy to test in isolation.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers time (HH:MM) and date as the primary constraints. Tasks are sorted chronologically so the owner always sees what comes next. Frequency (once, daily, weekly) determines whether a new task is created after completion. I prioritized time and date because those are the constraints a pet owner actually acts on day-to-day.

**b. Tradeoffs**

Conflict detection uses exact time matching — two tasks conflict only if they share the exact same HH:MM string and date. It does not check for overlapping durations (for example, a 30-minute walk at 09:00 and a vet appointment at 09:15 would not be flagged). This is a reasonable tradeoff for v1 because tasks in this system do not have durations. Adding duration-based overlap detection would require each task to store a duration and use interval comparison logic, which adds complexity without much benefit at this stage.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI for design brainstorming (drafting the UML and class responsibilities) and scaffolding (generating method stubs from the diagram). The most useful prompts were specific and referenced the actual file — for example asking "based on my skeletons in pawpal_system.py, how should Scheduler retrieve tasks from Owner?" rather than asking generically about scheduling systems.

**b. Judgment and verification**

When generating conflict detection, the AI initially suggested a nested loop that compared every task against every other task. I replaced it with a dictionary-based approach that groups tasks by (time, date) tuple. The dict approach is faster (O(n) vs O(n²)), easier to read, and simpler to extend. I verified the logic by writing a test that checks for a known conflict and a separate test that confirms no false positives on a clean schedule.

---

## 4. Testing and Verification

**a. What you tested**

- Task completion: mark_complete() flips the completed flag
- Task addition: adding a task increases the pet's task count
- Recurrence: daily tasks recur tomorrow, weekly tasks recur in 7 days, one-time tasks return None
- Scheduler integration: recurring tasks are added back to the correct pet after completion
- Sorting: tasks are returned in chronological HH:MM order
- Filtering: by status and by pet name, including edge cases like unknown pet names
- Conflict detection: flags overlapping times, no false positives on clean schedules
- Owner/Pet management: add, retrieve (case-insensitive), and remove pets

These tests matter because they cover both the happy path and edge cases that could silently break the scheduler.

**b. Confidence**

16/16 tests passing. Confidence level: 5/5 for the behaviors tested. The main gap is duration-based conflict detection, which is not implemented and therefore not tested.

---

## 5. Reflection

**a. What went well**

The layered architecture worked cleanly. Because Scheduler only depends on Owner and never directly touches Pet or Task internals, it was easy to test in isolation and easy to wire up to the Streamlit UI without any changes to the logic layer.

**b. What you would improve**

I would add a duration field to Task and upgrade conflict detection to check for overlapping time ranges rather than exact matches. I would also add persistent storage so the schedule survives a page refresh in Streamlit.

**c. Key takeaway**

AI tools are fast at generating syntactically correct code but default to the most generic pattern. The most important skill when working with AI is knowing enough to evaluate what comes back — the nested loop vs dictionary tradeoff in conflict detection is a good example of a case where the AI's first answer worked but was not the best answer.