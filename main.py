from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def print_section(title: str) -> None:
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


def main():
    owner = Owner("Mahad")
    buddy = Pet("Buddy", "Dog", 3)
    whiskers = Pet("Whiskers", "Cat", 5)
    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    today = date.today()

    buddy.add_task(Task("Morning walk", "07:30", "daily", "Buddy", today))
    buddy.add_task(Task("Breakfast feeding", "08:00", "daily", "Buddy", today))
    buddy.add_task(Task("Vet appointment", "14:00", "once", "Buddy", today))

    whiskers.add_task(Task("Breakfast feeding", "08:00", "daily", "Whiskers", today))
    whiskers.add_task(Task("Evening play", "18:30", "daily", "Whiskers", today))
    whiskers.add_task(Task("Flea medication", "09:00", "weekly", "Whiskers", today))

    scheduler = Scheduler(owner)

    print_section("Today's Schedule (sorted by time)")
    for task in scheduler.todays_schedule():
        print(f"  {task}")

    print_section("Conflict Detection")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for w in conflicts:
            print(f"  {w}")
    else:
        print("  No conflicts detected.")

    print_section("Incomplete Tasks")
    for task in scheduler.filter_by_status(completed=False):
        print(f"  {task}")

    print_section("Marking 'Morning walk' complete (daily, should recur)")
    walk = scheduler.filter_by_pet("Buddy")[0]
    scheduler.mark_task_complete(walk)
    print(f"  Marked: {walk.description} | completed={walk.completed}")
    print(f"  Buddy now has {len(scheduler.filter_by_pet('Buddy'))} tasks")

    print_section("Whiskers' Tasks")
    for task in scheduler.filter_by_pet("Whiskers"):
        print(f"  {task}")


if __name__ == "__main__":
    main()