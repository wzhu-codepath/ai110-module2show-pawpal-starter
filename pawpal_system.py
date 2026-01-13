from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date, timedelta
from enum import Enum


class Frequency(Enum):
    """Task frequency options."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    AS_NEEDED = "as_needed"


@dataclass
class Task:
    """Represents a task for a pet."""
    name: str
    duration: float  # in minutes
    priority: int  # 1-5, where 5 is highest
    taskType: str
    frequency: Frequency = Frequency.DAILY
    completed: bool = False
    last_completed: date = None
    time: str = None  # scheduled time in HH:MM format (e.g., "09:30")
    
    def isDueToday(self) -> bool:
        """Check if the task is due today based on frequency."""
        today = date.today()
        
        if self.frequency == Frequency.DAILY:
            return self.last_completed != today
        elif self.frequency == Frequency.WEEKLY:
            return self.last_completed is None or (today - self.last_completed).days >= 7
        elif self.frequency == Frequency.MONTHLY:
            return self.last_completed is None or (today.month != self.last_completed.month)
        else:  # AS_NEEDED
            return True
    
    def mark_complete(self) -> Optional['Task']:
        """
        Mark the task as complete and return a new task instance for the next occurrence.
        For daily/weekly tasks, creates a new instance with the next due date.
        For as_needed/monthly tasks, just marks as complete without creating a new instance.
        
        Returns:
            A new Task instance for the next occurrence (or None for as_needed/monthly tasks).
        """
        self.completed = True
        self.last_completed = date.today()
        
        # Only auto-create new instances for DAILY and WEEKLY tasks
        if self.frequency == Frequency.DAILY:
            next_date = date.today() + timedelta(days=1)
            return self._create_next_instance(next_date)
        elif self.frequency == Frequency.WEEKLY:
            next_date = date.today() + timedelta(weeks=1)
            return self._create_next_instance(next_date)
        else:
            # AS_NEEDED and MONTHLY tasks don't auto-generate
            return None
    
    def _create_next_instance(self, next_due_date: date) -> 'Task':
        """
        Create a new Task instance for the next occurrence.
        
        Args:
            next_due_date: The date when the new task should be due.
        
        Returns:
            A new Task instance with reset completion status.
        """
        return Task(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            taskType=self.taskType,
            frequency=self.frequency,
            completed=False,
            last_completed=None,
            time=self.time
        )


@dataclass
class Pet:
    """Represents a pet owned by an owner."""
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)
    
    def addTask(self, task: Task) -> None:
        """Add a task to the pet's task list."""
        self.tasks.append(task)
    
    def getTasks(self) -> List[Task]:
        """Get all tasks for the pet."""
        return self.tasks
    
    def getTasksByType(self, taskType: str) -> List[Task]:
        """Get tasks filtered by type."""
        return [task for task in self.tasks if task.taskType == taskType]
    
    def getTasksDueToday(self) -> List[Task]:
        """Get tasks that are due today."""
        return [task for task in self.tasks if task.isDueToday()]
    
    def complete_task(self, task: Task) -> Optional[Task]:
        """
        Mark a task as complete and add the next occurrence if applicable.
        
        Args:
            task: The task to mark as complete.
        
        Returns:
            The next Task instance if one was created, or None otherwise.
        """
        next_task = task.mark_complete()
        if next_task:
            self.addTask(next_task)
        return next_task


class Owner:
    """Represents a pet owner who manages multiple pets."""
    
    def __init__(self, name: str, dailyTimeAval: float):
        self.name = name
        self.dailyTimeAval = dailyTimeAval  # in minutes
        self.pets: List[Pet] = []
    
    def updateTimeAval(self, time: float) -> None:
        """Update the daily time availability."""
        self.dailyTimeAval = time
    
    def addPet(self, pet: Pet) -> None:
        """Add a pet to the owner's list."""
        self.pets.append(pet)
    
    def getPets(self) -> List[Pet]:
        """Get all pets owned by this owner."""
        return self.pets
    
    def getAllTasks(self) -> List[Task]:
        """Get all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.getTasks())
        return all_tasks
    
    def getTasksDueToday(self) -> List[tuple]:
        """Get all tasks due today, organized by pet. Returns list of (Pet, List[Task]) tuples."""
        tasks_by_pet = []
        for pet in self.pets:
            due_tasks = pet.getTasksDueToday()
            if due_tasks:
                tasks_by_pet.append((pet, due_tasks))
        return tasks_by_pet
    
    def getTasksByCompletionStatus(self, completed: bool) -> List[Task]:
        """Filter all tasks by completion status. Returns tasks that are completed or incomplete based on the parameter."""
        all_tasks = self.getAllTasks()
        return [task for task in all_tasks if task.completed == completed]
    
    def getTasksByPetName(self, pet_name: str) -> List[Task]:
        """Get all tasks for a pet by its name."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet.getTasks()
        return []


class Scheduler:
    """The "Brain" that retrieves, organizes, and manages tasks across pets."""
    
    def __init__(self, owner: Owner):
        self.owner = owner
        self.schedule: Dict[Pet, List[Task]] = {}
        self.conflicts: List[str] = []  # Store conflict warnings
    
    def genDailyPlan(self) -> List[tuple]:
        """Generate a daily plan for all pets based on owner availability. Returns list of (Pet, List[Task]) tuples."""
        schedule_list = self.owner.getTasksDueToday()
        
        # Prioritize tasks for each pet
        self.schedule = {}
        for pet, tasks in schedule_list:
            self.schedule[id(pet)] = (pet, self.prioritizeTasks(tasks))
        
        # Detect conflicts after scheduling
        self.conflicts = self.detectScheduleConflicts()
        
        return schedule_list
    
    def prioritizeTasks(self, tasks: List[Task]) -> List[Task]:
        """Prioritize tasks based on priority and constraints."""
        # Sort by priority (highest first), then by duration (shortest first)
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (-t.priority, t.duration)
        )
        
        # Check if tasks fit within owner's available time
        total_duration = 0
        scheduled_tasks = []
        
        for task in sorted_tasks:
            if total_duration + task.duration <= self.owner.dailyTimeAval:
                scheduled_tasks.append(task)
                total_duration += task.duration
        
        return scheduled_tasks
    
    def sortByTime(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks chronologically by scheduled time in HH:MM format."""
        def parse_time(time_str: str) -> int:
            """Convert HH:MM format to minutes since midnight for sorting."""
            if not time_str:
                return float('inf')  # Tasks without time go to the end
            try:
                hours, minutes = map(int, time_str.split(':'))
                return hours * 60 + minutes
            except (ValueError, AttributeError):
                return float('inf')
        
        return sorted(tasks, key=lambda t: parse_time(t.time))
    
    def detectScheduleConflicts(self) -> List[str]:
        """
        Detect and return warnings for tasks scheduled at the same time.
        Lightweight approach: returns warning messages without crashing.
        
        Returns:
            A list of warning messages describing detected conflicts.
        """
        warnings = []
        
        # Build a map of time -> [(pet_name, task_name), ...]
        time_map: Dict[str, List[Tuple[str, str]]] = {}
        
        for pet_id, (pet, tasks) in self.schedule.items():
            for task in tasks:
                if task.time:  # Only check tasks with scheduled times
                    if task.time not in time_map:
                        time_map[task.time] = []
                    time_map[task.time].append((pet.name, task.name))
        
        # Check for conflicts (multiple tasks at same time)
        for scheduled_time, task_list in time_map.items():
            if len(task_list) > 1:
                # Build warning message
                task_details = ", ".join([f"{task_name} ({pet_name})" for pet_name, task_name in task_list])
                warning = f"⚠️  Conflict at {scheduled_time}: {task_details}"
                warnings.append(warning)
        
        return warnings
    
    def getConflictWarnings(self) -> List[str]:
        """Return the list of conflict warnings from the last generated plan."""
        return self.conflicts
    
    def explainPlan(self) -> str:
        """Explain the generated daily plan, including any scheduling conflicts."""
        if not self.schedule:
            return "No tasks scheduled for today."
        
        explanation = f"Daily Plan for {self.owner.name}:\n"
        explanation += f"Available time: {self.owner.dailyTimeAval} minutes\n\n"
        
        total_time = 0
        for pet_id, (pet, tasks) in self.schedule.items():
            explanation += f"{pet.name} ({pet.species}):\n"
            for task in tasks:
                explanation += f"  - {task.name} ({task.duration} min) [Priority: {task.priority}]"
                if task.time:
                    explanation += f" @ {task.time}"
                explanation += "\n"
                total_time += task.duration
            explanation += "\n"
        
        explanation += f"Total time needed: {total_time} minutes\n"
        
        # Add conflict warnings if any exist
        if self.conflicts:
            explanation += "\n" + "=" * 50 + "\n"
            explanation += "SCHEDULING CONFLICTS DETECTED:\n"
            explanation += "=" * 50 + "\n"
            for warning in self.conflicts:
                explanation += warning + "\n"
            explanation += "Please review and reschedule conflicting tasks.\n"
        
        return explanation
    
    def getScheduledTasksByCompletionStatus(self, completed: bool) -> List[Task]:
        """Filter scheduled tasks by completion status."""
        scheduled_tasks = []
        for pet_id, (pet, tasks) in self.schedule.items():
            scheduled_tasks.extend([task for task in tasks if task.completed == completed])
        return scheduled_tasks
