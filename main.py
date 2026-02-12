from pawpal_system import Owner, Pet, Task, Scheduler, Frequency


def main():
    """Main script to demonstrate the PawPal scheduling system."""
    
    # Create an owner
    owner = Owner("Alice")
    
    # Create pets
    dog = Pet("Max", "Golden Retriever")
    
    # Add pets to owner
    owner.addPet(dog)
    
    # Create tasks for the dog
    walk_task = Task(
        name="Morning Walk",
        duration=45,
        priority=5,
        taskType="Exercise",
        frequency=Frequency.DAILY,
        time="09:00"  # Scheduled at 9:00 AM
    )
    
    feed_task = Task(
        name="Feeding",
        duration=10,
        priority=5,
        taskType="Feeding",
        frequency=Frequency.DAILY,
        time="08:00"  # Scheduled at 8:00 AM
    )
    
    # Add tasks to dog
    dog.addTask(walk_task)
    dog.addTask(feed_task)
    
    # Create scheduler and generate daily plan
    scheduler = Scheduler(owner)
    scheduler.genDailyPlan()
    
    # Print today's schedule
    print("=" * 60)
    print("TODAY'S SCHEDULE")
    print("=" * 60)
    print(scheduler.explainPlan())
    print("=" * 60)


if __name__ == "__main__":
    main()
