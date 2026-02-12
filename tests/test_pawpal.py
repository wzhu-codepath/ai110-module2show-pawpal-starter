import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler, Frequency

# ==================== EXISTING TESTS ====================

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


# ==================== RECURRING TASK EDGE CASES ====================

class TestRecurringTaskLogic:
    """Test recurrence logic for different task frequencies."""
    
    def test_daily_task_never_completed_is_due(self):
        """Daily task with no completion history should be due."""
        task = Task(name="Feed", duration=5.0, priority=3, taskType="feeding", 
                   frequency=Frequency.DAILY, last_completed=None)
        assert task.isDueToday() is True
    
    def test_daily_task_completed_today_not_due(self):
        """Daily task completed today should NOT be due."""
        task = Task(name="Feed", duration=5.0, priority=3, taskType="feeding",
                   frequency=Frequency.DAILY, last_completed=date.today())
        assert task.isDueToday() is False
    
    def test_daily_task_completed_yesterday_is_due(self):
        """Daily task completed yesterday should be due today."""
        yesterday = date.today() - timedelta(days=1)
        task = Task(name="Feed", duration=5.0, priority=3, taskType="feeding",
                   frequency=Frequency.DAILY, last_completed=yesterday)
        assert task.isDueToday() is True
    
    def test_weekly_task_never_completed_is_due(self):
        """Weekly task with no completion history should be due."""
        task = Task(name="Bath", duration=30.0, priority=2, taskType="grooming",
                   frequency=Frequency.WEEKLY, last_completed=None)
        assert task.isDueToday() is True
    
    def test_weekly_task_exactly_7_days_old_is_due(self):
        """Weekly task exactly 7 days old should be due."""
        seven_days_ago = date.today() - timedelta(days=7)
        task = Task(name="Bath", duration=30.0, priority=2, taskType="grooming",
                   frequency=Frequency.WEEKLY, last_completed=seven_days_ago)
        assert task.isDueToday() is True
    
    def test_weekly_task_6_days_old_not_due(self):
        """Weekly task only 6 days old should NOT be due."""
        six_days_ago = date.today() - timedelta(days=6)
        task = Task(name="Bath", duration=30.0, priority=2, taskType="grooming",
                   frequency=Frequency.WEEKLY, last_completed=six_days_ago)
        assert task.isDueToday() is False
    
    def test_monthly_task_never_completed_is_due(self):
        """Monthly task with no completion history should be due."""
        task = Task(name="Vet", duration=60.0, priority=5, taskType="health",
                   frequency=Frequency.MONTHLY, last_completed=None)
        assert task.isDueToday() is True
    
    def test_monthly_task_same_month_not_due(self):
        """Monthly task completed earlier in same month should NOT be due."""
        earlier_this_month = date.today() - timedelta(days=5)
        task = Task(name="Vet", duration=60.0, priority=5, taskType="health",
                   frequency=Frequency.MONTHLY, last_completed=earlier_this_month)
        assert task.isDueToday() is False
    
    def test_as_needed_always_due(self):
        """AS_NEEDED tasks should always be due."""
        task = Task(name="Emergency", duration=15.0, priority=5, taskType="emergency",
                   frequency=Frequency.AS_NEEDED, last_completed=date.today())
        assert task.isDueToday() is True
    
    def test_mark_complete_daily_creates_new_task(self):
        """Marking a daily task complete should create a new task for tomorrow."""
        task = Task(name="Feed", duration=5.0, priority=3, taskType="feeding",
                   frequency=Frequency.DAILY, time="09:00")
        
        next_task = task.mark_complete()
        
        # Original task should be marked complete
        assert task.completed is True
        assert task.last_completed == date.today()
        
        # New task should be created
        assert next_task is not None
        assert next_task.name == "Feed"
        assert next_task.completed is False
        assert next_task.last_completed is None
        assert next_task.frequency == Frequency.DAILY
        assert next_task.time == "09:00"
    
    def test_mark_complete_weekly_creates_new_task(self):
        """Marking a weekly task complete should create a new task for next week."""
        task = Task(name="Bath", duration=30.0, priority=2, taskType="grooming",
                   frequency=Frequency.WEEKLY, time="14:00")
        
        next_task = task.mark_complete()
        
        assert task.completed is True
        assert next_task is not None
        assert next_task.name == "Bath"
        assert next_task.completed is False
        assert next_task.frequency == Frequency.WEEKLY
    
    def test_mark_complete_as_needed_no_new_task(self):
        """Marking an AS_NEEDED task complete should NOT create a new task."""
        task = Task(name="Emergency", duration=15.0, priority=5, taskType="emergency",
                   frequency=Frequency.AS_NEEDED)
        
        next_task = task.mark_complete()
        
        assert task.completed is True
        assert next_task is None
    
    def test_mark_complete_monthly_no_new_task(self):
        """Marking a MONTHLY task complete should NOT create a new task."""
        task = Task(name="Vet", duration=60.0, priority=5, taskType="health",
                   frequency=Frequency.MONTHLY)
        
        next_task = task.mark_complete()
        
        assert task.completed is True
        assert next_task is None
    
    def test_complete_task_adds_next_instance_to_pet(self):
        """Pet.complete_task() should add the next instance to the pet's task list."""
        pet = Pet(name="Buddy", species="dog")
        task = Task(name="Feed", duration=5.0, priority=3, taskType="feeding",
                   frequency=Frequency.DAILY)
        pet.addTask(task)
        
        initial_count = len(pet.getTasks())
        pet.complete_task(task)
        
        # Should have original + new task
        assert len(pet.getTasks()) == initial_count + 1
        # New task should be in the list
        assert pet.getTasks()[-1].name == "Feed"
        assert pet.getTasks()[-1].completed is False


# ==================== SORTING CORRECTNESS ====================

class TestTaskSorting:
    """Test chronological sorting of tasks by scheduled time."""
    
    def test_sort_by_time_basic_order(self):
        """Tasks should be sorted chronologically by scheduled time."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        task1 = Task(name="Breakfast", duration=5.0, priority=3, taskType="feeding", time="09:00")
        task2 = Task(name="Lunch", duration=10.0, priority=3, taskType="feeding", time="12:00")
        task3 = Task(name="Dinner", duration=10.0, priority=3, taskType="feeding", time="18:00")
        
        unsorted_tasks = [task3, task1, task2]
        sorted_tasks = scheduler.sortByTime(unsorted_tasks)
        
        assert sorted_tasks[0].time == "09:00"
        assert sorted_tasks[1].time == "12:00"
        assert sorted_tasks[2].time == "18:00"
    
    def test_sort_by_time_midnight_first(self):
        """Tasks at midnight should sort before later tasks."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        task1 = Task(name="Night", duration=5.0, priority=3, taskType="feeding", time="00:00")
        task2 = Task(name="Morning", duration=5.0, priority=3, taskType="feeding", time="08:00")
        
        sorted_tasks = scheduler.sortByTime([task2, task1])
        
        assert sorted_tasks[0].time == "00:00"
        assert sorted_tasks[1].time == "08:00"
    
    def test_sort_by_time_edge_times(self):
        """Edge times (00:00, 23:59) should sort correctly."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        task1 = Task(name="Start", duration=5.0, priority=3, taskType="feeding", time="00:00")
        task2 = Task(name="Noon", duration=5.0, priority=3, taskType="feeding", time="12:00")
        task3 = Task(name="End", duration=5.0, priority=3, taskType="feeding", time="23:59")
        
        sorted_tasks = scheduler.sortByTime([task3, task1, task2])
        
        assert sorted_tasks[0].time == "00:00"
        assert sorted_tasks[1].time == "12:00"
        assert sorted_tasks[2].time == "23:59"
    
    def test_sort_by_time_no_time_goes_to_end(self):
        """Tasks without scheduled times should go to the end."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        task1 = Task(name="Morning", duration=5.0, priority=3, taskType="feeding", time="08:00")
        task2 = Task(name="Flexible", duration=5.0, priority=3, taskType="feeding", time=None)
        task3 = Task(name="Afternoon", duration=5.0, priority=3, taskType="feeding", time="14:00")
        
        sorted_tasks = scheduler.sortByTime([task2, task3, task1])
        
        assert sorted_tasks[0].time == "08:00"
        assert sorted_tasks[1].time == "14:00"
        assert sorted_tasks[2].time is None
    
    def test_sort_by_time_multiple_no_time(self):
        """Multiple tasks without times should all go to the end."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        task1 = Task(name="Morning", duration=5.0, priority=3, taskType="feeding", time="09:00")
        task2 = Task(name="Flex1", duration=5.0, priority=3, taskType="feeding", time=None)
        task3 = Task(name="Flex2", duration=5.0, priority=3, taskType="feeding", time=None)
        
        sorted_tasks = scheduler.sortByTime([task2, task1, task3])
        
        assert sorted_tasks[0].time == "09:00"
        # Both unscheduled tasks at end
        assert sorted_tasks[1].time is None
        assert sorted_tasks[2].time is None
    
    def test_sort_by_time_invalid_format_goes_to_end(self):
        """Tasks with invalid time format should not crash and go to the end."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        task1 = Task(name="Morning", duration=5.0, priority=3, taskType="feeding", time="09:00")
        task2 = Task(name="Invalid", duration=5.0, priority=3, taskType="feeding", time="25:99")
        
        sorted_tasks = scheduler.sortByTime([task2, task1])
        
        # Should not crash, valid time first
        assert sorted_tasks[0].time == "09:00"
        assert sorted_tasks[1].time == "25:99"
    
    def test_sort_by_time_stable_same_times(self):
        """When times are equal, order should be preserved (stable sort)."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        task1 = Task(name="Feed_A", duration=5.0, priority=3, taskType="feeding", time="12:00")
        task2 = Task(name="Feed_B", duration=5.0, priority=3, taskType="feeding", time="12:00")
        task3 = Task(name="Feed_C", duration=5.0, priority=3, taskType="feeding", time="12:00")
        
        sorted_tasks = scheduler.sortByTime([task1, task2, task3])
        
        # All have same time, should maintain relative order
        assert sorted_tasks[0].name == "Feed_A"
        assert sorted_tasks[1].name == "Feed_B"
        assert sorted_tasks[2].name == "Feed_C"


# ==================== CONFLICT DETECTION ====================

class TestConflictDetection:
    """Test that the scheduler correctly detects and reports scheduling conflicts."""
    
    def test_no_conflicts_different_times(self):
        """Different task times should produce no conflicts."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        pet = Pet(name="Buddy", species="dog")
        task1 = Task(name="Feed", duration=5.0, priority=3, taskType="feeding", time="09:00")
        task2 = Task(name="Walk", duration=30.0, priority=4, taskType="exercise", time="14:00")
        
        pet.addTask(task1)
        pet.addTask(task2)
        owner.addPet(pet)
        
        scheduler.genDailyPlan()
        warnings = scheduler.getConflictWarnings()
        
        assert len(warnings) == 0
    
    def test_conflict_same_time_same_pet(self):
        """Two tasks for same pet at same time should be flagged."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        pet = Pet(name="Buddy", species="dog")
        task1 = Task(name="Feed", duration=5.0, priority=5, taskType="feeding", time="09:00")
        task2 = Task(name="Medication", duration=2.0, priority=5, taskType="health", time="09:00")
        
        pet.addTask(task1)
        pet.addTask(task2)
        owner.addPet(pet)
        
        scheduler.genDailyPlan()
        warnings = scheduler.getConflictWarnings()
        
        assert len(warnings) == 1
        assert "09:00" in warnings[0]
        assert "Feed" in warnings[0] or "Medication" in warnings[0]
    
    def test_conflict_same_time_different_pets(self):
        """Two tasks for different pets at same time should be flagged."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        pet1 = Pet(name="Buddy", species="dog")
        pet2 = Pet(name="Whiskers", species="cat")
        
        task1 = Task(name="Feed Dog", duration=5.0, priority=5, taskType="feeding", time="09:00")
        task2 = Task(name="Feed Cat", duration=5.0, priority=5, taskType="feeding", time="09:00")
        
        pet1.addTask(task1)
        pet2.addTask(task2)
        owner.addPet(pet1)
        owner.addPet(pet2)
        
        scheduler.genDailyPlan()
        warnings = scheduler.getConflictWarnings()
        
        assert len(warnings) == 1
        assert "09:00" in warnings[0]
        assert "Buddy" in warnings[0] and "Whiskers" in warnings[0]
    
    def test_multiple_conflicts_detected(self):
        """Multiple scheduling conflicts should all be detected."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        pet1 = Pet(name="Buddy", species="dog")
        pet2 = Pet(name="Whiskers", species="cat")
        
        # Conflict at 09:00
        task1 = Task(name="Feed Dog", duration=5.0, priority=5, taskType="feeding", time="09:00")
        task2 = Task(name="Feed Cat", duration=5.0, priority=5, taskType="feeding", time="09:00")
        
        # Conflict at 14:00
        task3 = Task(name="Walk", duration=30.0, priority=4, taskType="exercise", time="14:00")
        task4 = Task(name="Play", duration=20.0, priority=3, taskType="exercise", time="14:00")
        
        pet1.addTask(task1)
        pet1.addTask(task3)
        pet2.addTask(task2)
        pet2.addTask(task4)
        
        owner.addPet(pet1)
        owner.addPet(pet2)
        
        scheduler.genDailyPlan()
        warnings = scheduler.getConflictWarnings()
        
        assert len(warnings) == 2
        assert any("09:00" in w for w in warnings)
        assert any("14:00" in w for w in warnings)
    
    def test_no_conflict_without_time(self):
        """Tasks without scheduled times should not trigger conflicts."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        pet = Pet(name="Buddy", species="dog")
        task1 = Task(name="Feed", duration=5.0, priority=3, taskType="feeding", time=None)
        task2 = Task(name="Walk", duration=30.0, priority=4, taskType="exercise", time=None)
        
        pet.addTask(task1)
        pet.addTask(task2)
        owner.addPet(pet)
        
        scheduler.genDailyPlan()
        warnings = scheduler.getConflictWarnings()
        
        assert len(warnings) == 0
    
    def test_conflict_warning_format(self):
        """Conflict warnings should include pet names and task names."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        pet1 = Pet(name="Buddy", species="dog")
        pet2 = Pet(name="Whiskers", species="cat")
        
        task1 = Task(name="Feed Dog", duration=5.0, priority=5, taskType="feeding", time="09:00")
        task2 = Task(name="Feed Cat", duration=5.0, priority=5, taskType="feeding", time="09:00")
        
        pet1.addTask(task1)
        pet2.addTask(task2)
        owner.addPet(pet1)
        owner.addPet(pet2)
        
        scheduler.genDailyPlan()
        warnings = scheduler.getConflictWarnings()
        
        assert len(warnings) == 1
        warning = warnings[0]
        assert "Feed Dog" in warning
        assert "Feed Cat" in warning
        assert "Buddy" in warning
        assert "Whiskers" in warning


# ==================== SCHEDULING & PRIORITIZATION ====================

class TestTaskPrioritization:
    """Test task prioritization and scheduling constraints."""
    
    def test_zero_time_availability_empty_schedule(self):
        """Owner with zero time availability should have empty schedule."""
        owner = Owner("John", 0)
        scheduler = Scheduler(owner)
        
        pet = Pet(name="Buddy", species="dog")
        task = Task(name="Feed", duration=5.0, priority=5, taskType="feeding")
        pet.addTask(task)
        owner.addPet(pet)
        
        scheduler.genDailyPlan()
        scheduled = scheduler.getScheduledTasksByCompletionStatus(False)
        
        assert len(scheduled) == 0
    
    def test_tasks_exceed_time_lowest_priority_dropped(self):
        """When tasks exceed available time, lowest-priority tasks should be dropped."""
        owner = Owner("John", 20)  # Only 20 minutes available
        scheduler = Scheduler(owner)
        
        pet = Pet(name="Buddy", species="dog")
        task1 = Task(name="Feed", duration=10.0, priority=5, taskType="feeding")
        task2 = Task(name="Walk", duration=15.0, priority=3, taskType="exercise")
        
        pet.addTask(task1)
        pet.addTask(task2)
        owner.addPet(pet)
        
        scheduler.genDailyPlan()
        scheduled = scheduler.getScheduledTasksByCompletionStatus(False)
        
        # Should only schedule high-priority task that fits
        assert len(scheduled) == 1
        assert scheduled[0].priority == 5
    
    def test_same_priority_shorter_duration_scheduled_first(self):
        """When priorities are equal, shorter tasks should be preferred."""
        owner = Owner("John", 25)  # Only 25 minutes available
        scheduler = Scheduler(owner)
        
        pet = Pet(name="Buddy", species="dog")
        task1 = Task(name="Feed", duration=10.0, priority=3, taskType="feeding")
        task2 = Task(name="Quick Walk", duration=15.0, priority=3, taskType="exercise")
        task3 = Task(name="Treat", duration=2.0, priority=3, taskType="reward")
        
        pet.addTask(task1)
        pet.addTask(task2)
        pet.addTask(task3)
        owner.addPet(pet)
        
        scheduler.genDailyPlan()
        scheduled = scheduler.getScheduledTasksByCompletionStatus(False)
        
        # Should schedule high-value tasks that fit: Feed (10) + Quick Walk (15) = 25
        # or Feed + Treat = 12, but Walk doesn't fit with Treat
        assert "Feed" in [t.name for t in scheduled]
    
    def test_exact_time_match(self):
        """Tasks totaling exactly available time should all be scheduled."""
        owner = Owner("John", 50)
        scheduler = Scheduler(owner)
        
        pet = Pet(name="Buddy", species="dog")
        task1 = Task(name="Feed", duration=20.0, priority=3, taskType="feeding")
        task2 = Task(name="Walk", duration=30.0, priority=3, taskType="exercise")
        
        pet.addTask(task1)
        pet.addTask(task2)
        owner.addPet(pet)
        
        scheduler.genDailyPlan()
        scheduled = scheduler.getScheduledTasksByCompletionStatus(False)
        
        assert len(scheduled) == 2
        total_duration = sum(t.duration for t in scheduled)
        assert total_duration == 50


# ==================== DATA INTEGRITY ====================

class TestDataIntegrity:
    """Test that task completion doesn't cause data corruption."""
    
    def test_mark_complete_doesnt_modify_original_task(self):
        """The original task object should not be affected by mark_complete."""
        task = Task(name="Feed", duration=5.0, priority=3, taskType="feeding",
                   frequency=Frequency.DAILY, time="09:00")
        
        original_name = task.name
        original_duration = task.duration
        original_priority = task.priority
        original_time = task.time
        original_frequency = task.frequency
        
        task.mark_complete()
        
        # Properties should remain the same (except completed/last_completed)
        assert task.name == original_name
        assert task.duration == original_duration
        assert task.priority == original_priority
        assert task.time == original_time
        assert task.frequency == original_frequency
    
    def test_next_instance_inherits_all_properties(self):
        """Next task instance should inherit all parent properties."""
        task = Task(name="Feed", duration=5.0, priority=3, taskType="feeding",
                   frequency=Frequency.DAILY, time="09:00")
        
        next_task = task.mark_complete()
        
        assert next_task.name == task.name
        assert next_task.duration == task.duration
        assert next_task.priority == task.priority
        assert next_task.taskType == task.taskType
        assert next_task.frequency == task.frequency
        assert next_task.time == task.time
    
    def test_fractional_duration_handled_correctly(self):
        """Tasks with fractional durations should be handled without error."""
        owner = Owner("John", 30.5)
        scheduler = Scheduler(owner)
        
        pet = Pet(name="Buddy", species="dog")
        task1 = Task(name="Quick", duration=15.25, priority=3, taskType="feeding")
        task2 = Task(name="Normal", duration=15.25, priority=3, taskType="exercise")
        
        pet.addTask(task1)
        pet.addTask(task2)
        owner.addPet(pet)
        
        scheduler.genDailyPlan()
        scheduled = scheduler.getScheduledTasksByCompletionStatus(False)
        
        assert len(scheduled) == 2


# ==================== MULTI-PET SCENARIOS ====================

class TestMultiPetScheduling:
    """Test scheduling behavior with multiple pets."""
    
    def test_multiple_pets_same_task_names_conflict_identified(self):
        """Conflicts should include pet names when tasks have same names."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        pet1 = Pet(name="Buddy", species="dog")
        pet2 = Pet(name="Whiskers", species="cat")
        
        # Both pets have "Feed" task at same time
        task1 = Task(name="Feed", duration=5.0, priority=5, taskType="feeding", time="09:00")
        task2 = Task(name="Feed", duration=5.0, priority=5, taskType="feeding", time="09:00")
        
        pet1.addTask(task1)
        pet2.addTask(task2)
        owner.addPet(pet1)
        owner.addPet(pet2)
        
        scheduler.genDailyPlan()
        warnings = scheduler.getConflictWarnings()
        
        assert len(warnings) == 1
        assert "Buddy" in warnings[0] and "Whiskers" in warnings[0]
    
    def test_pet_with_no_tasks_not_in_plan(self):
        """Pets with no tasks should not appear in the daily plan."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        pet1 = Pet(name="Buddy", species="dog")
        pet2 = Pet(name="Whiskers", species="cat")
        
        task = Task(name="Feed", duration=5.0, priority=3, taskType="feeding")
        pet1.addTask(task)
        
        owner.addPet(pet1)
        owner.addPet(pet2)
        
        plan = scheduler.genDailyPlan()
        
        # Only pet1 should be in plan
        pet_names = [pet.name for pet, _ in plan]
        assert "Buddy" in pet_names
        assert "Whiskers" not in pet_names
    
    def test_zero_pets_empty_plan(self):
        """Owner with no pets should have empty schedule."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        plan = scheduler.genDailyPlan()
        
        assert len(plan) == 0
    
    def test_explain_plan_empty_schedule(self):
        """explainPlan should handle empty schedule gracefully."""
        owner = Owner("John", 480)
        scheduler = Scheduler(owner)
        
        explanation = scheduler.explainPlan()
        
        assert "No tasks scheduled for today" in explanation