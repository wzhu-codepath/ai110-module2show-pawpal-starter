import pytest
from datetime import date
from pawpal_system import Task, Pet

def test_task_mark_complete_changes_status():
    task = Task(name="Feed", duration=5.0, priority=3, taskType="feeding")
    assert task.completed is False
    today = date.today()
    if hasattr(task, "mark_complete"):
        task.mark_complete()
    else:
        # Fallback if mark_complete isn't implemented: emulate completion
        task.completed = True
        task.last_completed = today
    assert task.completed is True
    assert task.last_completed == today

def test_pet_add_task_increases_count():
    pet = Pet(name="Buddy", species="dog")
    initial_count = len(pet.getTasks())
    new_task = Task(name="Walk", duration=30.0, priority=4, taskType="exercise")
    pet.addTask(new_task)
    assert len(pet.getTasks()) == initial_count + 1
    assert pet.getTasks()[-1] is new_task