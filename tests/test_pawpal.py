import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


@pytest.fixture
def today():
    return date.today()


@pytest.fixture
def sample_owner(today):
    owner = Owner("Test Owner")
    dog = Pet("Rex", "Dog", 2)
    cat = Pet("Luna", "Cat", 4)
    dog.add_task(Task("Walk", "08:00", "daily", "Rex", today))
    dog.add_task(Task("Feed", "12:00", "daily", "Rex", today))
    dog.add_task(Task("Vet", "09:00", "once", "Rex", today))
    cat.add_task(Task("Feed", "08:00", "daily", "Luna", today))
    cat.add_task(Task("Play", "18:00", "weekly", "Luna", today))
    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner


@pytest.fixture
def scheduler(sample_owner):
    return Scheduler(sample_owner)


# Task tests

def test_mark_complete_changes_status(today):
    task = Task("Bath", "10:00", "once", "Rex", today)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count(today):
    pet = Pet("Fido", "Dog", 1)
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Walk", "07:00", "daily", "Fido", today))
    assert len(pet.get_tasks()) == 1


# Recurrence tests

def test_daily_task_recurs_tomorrow(today):
    task = Task("Walk", "07:00", "daily", "Rex", today)
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False


def test_weekly_task_recurs_next_week(today):
    task = Task("Grooming", "11:00", "weekly", "Rex", today)
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_once_task_no_recurrence(today):
    task = Task("Vet", "14:00", "once", "Rex", today)
    assert task.mark_complete() is None


def test_scheduler_adds_recurrence_to_pet(sample_owner, today):
    scheduler = Scheduler(sample_owner)
    pet = sample_owner.get_pet("Rex")
    original_count = len(pet.get_tasks())
    daily_task = next(t for t in pet.get_tasks() if t.frequency == "daily")
    scheduler.mark_task_complete(daily_task)
    assert len(pet.get_tasks()) == original_count + 1


# Sorting tests

def test_sort_by_time_is_chronological(scheduler):
    sorted_tasks = scheduler.sort_by_time()
    times = [t.time for t in sorted_tasks]
    assert times == sorted(times)


def test_sort_by_time_empty_list(scheduler):
    assert scheduler.sort_by_time([]) == []


# Filtering tests

def test_filter_by_status_incomplete(scheduler):
    incomplete = scheduler.filter_by_status(completed=False)
    assert all(not t.completed for t in incomplete)


def test_filter_by_pet_correct_tasks(scheduler):
    rex_tasks = scheduler.filter_by_pet("Rex")
    assert all(t.pet_name == "Rex" for t in rex_tasks)


def test_filter_by_pet_unknown_returns_empty(scheduler):
    assert scheduler.filter_by_pet("Nobody") == []


# Conflict detection tests

def test_detect_conflicts_finds_overlap(scheduler):
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) >= 1
    assert any("08:00" in w for w in conflicts)


def test_detect_conflicts_no_false_positives(today):
    owner = Owner("Clean")
    pet = Pet("Solo", "Dog", 1)
    pet.add_task(Task("Walk", "07:00", "daily", "Solo", today))
    pet.add_task(Task("Feed", "12:00", "daily", "Solo", today))
    owner.add_pet(pet)
    assert Scheduler(owner).detect_conflicts() == []


# Owner/Pet management tests

def test_owner_get_pet_case_insensitive():
    owner = Owner("Alex")
    owner.add_pet(Pet("Mochi", "Cat", 2))
    assert owner.get_pet("mochi") is not None


def test_owner_remove_pet():
    owner = Owner("Alex")
    owner.add_pet(Pet("Mochi", "Cat", 2))
    owner.add_pet(Pet("Coco", "Dog", 3))
    owner.remove_pet("Mochi")
    assert owner.get_pet("Mochi") is None
    assert len(owner.pets) == 1


def test_new_pet_has_no_tasks():
    assert Pet("Empty", "Fish", 1).get_tasks() == []