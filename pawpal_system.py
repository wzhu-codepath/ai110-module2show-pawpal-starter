from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime, date
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


class Scheduler:
    """The "Brain" that retrieves, organizes, and manages tasks across pets."""
    
    def __init__(self, owner: Owner):
        self.owner = owner
        self.schedule: Dict[Pet, List[Task]] = {}
    
    def genDailyPlan(self) -> List[tuple]:
        """Generate a daily plan for all pets based on owner availability. Returns list of (Pet, List[Task]) tuples."""
        schedule_list = self.owner.getTasksDueToday()
        
        # Prioritize tasks for each pet
        self.schedule = {}
        for pet, tasks in schedule_list:
            self.schedule[id(pet)] = (pet, self.prioritizeTasks(tasks))
        
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
    
    def explainPlan(self) -> str:
        """Explain the generated daily plan."""
        if not self.schedule:
            return "No tasks scheduled for today."
        
        explanation = f"Daily Plan for {self.owner.name}:\n"
        explanation += f"Available time: {self.owner.dailyTimeAval} minutes\n\n"
        
        total_time = 0
        for pet_id, (pet, tasks) in self.schedule.items():
            explanation += f"{pet.name} ({pet.species}):\n"
            for task in tasks:
                explanation += f"  - {task.name} ({task.duration} min) [Priority: {task.priority}]\n"
                total_time += task.duration
            explanation += "\n"
        
        explanation += f"Total time needed: {total_time} minutes\n"
        return explanation
